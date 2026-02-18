"""Email service for sending notifications and invitations.

Uses Resend (https://resend.com) for email delivery.
Resend offers:
- Generous free tier (100 emails/day)
- Simple API
- Good deliverability
- Domain verification for production

Alternative providers:
- SendGrid: More features, more complex
- AWS SES: Cheaper at scale, more setup
- Postmark: Good for transactional emails
"""
import logging
from typing import Optional, List
from dataclasses import dataclass

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EmailRecipient:
    """Email recipient with optional name."""
    email: str
    name: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to Resend API format."""
        if self.name:
            return {"email": self.email, "name": self.name}
        return {"email": self.email}


class EmailService:
    """Service for sending emails via Resend API."""
    
    def __init__(self):
        self.api_key: Optional[str] = getattr(settings, 'RESEND_API_KEY', None)
        self.from_email: str = getattr(
            settings, 
            'FROM_EMAIL', 
            'noreply@datarevolt.agency'
        )
        self.from_name: str = getattr(
            settings,
            'FROM_NAME',
            'DRA Reconciliation Platform'
        )
        self.enabled: bool = bool(self.api_key)
        
        if not self.enabled:
            logger.warning(
                "Email service not configured. "
                "Set RESEND_API_KEY to enable email notifications."
            )
    
    async def send_email(
        self,
        to: List[EmailRecipient],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc: Optional[List[EmailRecipient]] = None,
        bcc: Optional[List[EmailRecipient]] = None,
        reply_to: Optional[EmailRecipient] = None
    ) -> dict:
        """Send an email via Resend API.
        
        Args:
            to: List of recipients
            subject: Email subject
            html_content: HTML body content
            text_content: Plain text body content (optional)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            reply_to: Reply-to address (optional)
            
        Returns:
            API response with email ID
            
        Raises:
            EmailServiceError: If email sending fails
        """
        if not self.enabled:
            logger.info(
                f"Email would be sent (disabled): to={len(to)} recipients, "
                f"subject={subject}"
            )
            return {"id": "mock-email-id", "message": "Email service disabled"}
        
        # Build payload
        payload = {
            "from": f"{self.from_name} <{self.from_email}>",
            "to": [r.to_dict() for r in to],
            "subject": subject,
            "html": html_content,
        }
        
        if text_content:
            payload["text"] = text_content
        
        if cc:
            payload["cc"] = [r.to_dict() for r in cc]
        
        if bcc:
            payload["bcc"] = [r.to_dict() for r in bcc]
        
        if reply_to:
            payload["reply_to"] = reply_to.to_dict()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(
                    f"Email sent successfully",
                    extra={
                        "email_id": result.get("id"),
                        "to_count": len(to),
                        "subject": subject
                    }
                )
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Email API error: {e.response.status_code} - {e.response.text}",
                extra={
                    "status_code": e.response.status_code,
                    "subject": subject
                }
            )
            raise EmailServiceError(
                f"Failed to send email: {e.response.text}",
                status_code=e.response.status_code
            ) from e
        except Exception as e:
            logger.error(f"Email sending error: {e}", exc_info=True)
            raise EmailServiceError(f"Failed to send email: {e}") from e
    
    async def send_user_invitation(
        self,
        email: str,
        inviter_name: str,
        client_name: str,
        role: str,
        invite_link: Optional[str] = None
    ) -> dict:
        """Send user invitation email.
        
        Args:
            email: Recipient email address
            inviter_name: Name of the person sending the invite
            client_name: Name of the client/organization
            role: Role being assigned (admin, viewer)
            invite_link: Optional magic link for sign-up
            
        Returns:
            API response
        """
        role_display = "Administrator" if role == "admin" else "Viewer"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>You're Invited to DRA Reconciliation Platform</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #f9fafb;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .button {{
                    display: inline-block;
                    background: #dc2626;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: 600;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>You're Invited!</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                
                <p><strong>{inviter_name}</strong> has invited you to join 
                <strong>{client_name}</strong> on the DRA Transaction Reconciliation Platform.</p>
                
                <p>You'll have <strong>{role_display}</strong> access to view reconciliation 
                reports and track transaction data quality.</p>
                
                <p>With this platform, you can:</p>
                <ul>
                    <li>View match rates between your store and Google Analytics</li>
                    <li>Identify missing transactions</li>
                    <li>Track reconciliation trends over time</li>
                    <li>Export detailed reports</li>
                </ul>
                
                <center>
                    <a href="{invite_link or '#'}" class="button">
                        Accept Invitation
                    </a>
                </center>
                
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #6b7280;">
                    {invite_link or 'Contact your administrator for access'}
                </p>
                
                <p>This invitation will expire in 7 days.</p>
            </div>
            <div class="footer">
                <p>DRA Transaction Reconciliation Platform<br>
                Data Revolt Agency</p>
                <p>If you didn't expect this invitation, please ignore this email.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
You're Invited!

Hello,

{inviter_name} has invited you to join {client_name} on the DRA Transaction Reconciliation Platform.

You'll have {role_display} access to view reconciliation reports and track transaction data quality.

To accept this invitation, visit:
{invite_link or 'Contact your administrator for access'}

This invitation will expire in 7 days.

---
DRA Transaction Reconciliation Platform
Data Revolt Agency
"""
        
        return await self.send_email(
            to=[EmailRecipient(email=email)],
            subject=f"Invitation to join {client_name} on DRA Platform",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_job_completion_notification(
        self,
        email: str,
        client_name: str,
        job_id: int,
        match_rate: float,
        missing_count: int,
        dashboard_url: Optional[str] = None
    ) -> dict:
        """Send job completion notification email.
        
        Args:
            email: Recipient email address
            client_name: Name of the client
            job_id: The completed job ID
            match_rate: Match rate percentage
            missing_count: Number of missing transactions
            dashboard_url: URL to view results
            
        Returns:
            API response
        """
        status_color = "#22c55e" if match_rate >= 90 else "#eab308" if match_rate >= 70 else "#dc2626"
        status_text = "Excellent" if match_rate >= 90 else "Good" if match_rate >= 70 else "Needs Attention"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reconciliation Complete - {client_name}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #f9fafb;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .stats {{
                    display: flex;
                    justify-content: space-around;
                    margin: 20px 0;
                    text-align: center;
                }}
                .stat {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    flex: 1;
                    margin: 0 10px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .stat-value {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #dc2626;
                }}
                .stat-label {{
                    font-size: 12px;
                    color: #6b7280;
                    text-transform: uppercase;
                }}
                .button {{
                    display: inline-block;
                    background: #dc2626;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: 600;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Reconciliation Complete</h1>
                <p>{client_name}</p>
            </div>
            <div class="content">
                <p>Your transaction reconciliation has been completed successfully.</p>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value" style="color: {status_color}">{match_rate:.1f}%</div>
                        <div class="stat-label">Match Rate</div>
                        <div style="font-size: 12px; color: {status_color}; margin-top: 5px;">{status_text}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{missing_count}</div>
                        <div class="stat-label">Missing Transactions</div>
                    </div>
                </div>
                
                <center>
                    <a href="{dashboard_url or '#'}" class="button">
                        View Full Report
                    </a>
                </center>
                
                <p style="font-size: 14px; color: #6b7280; margin-top: 20px;">
                    Job ID: #{job_id}
                </p>
            </div>
            <div class="footer">
                <p>DRA Transaction Reconciliation Platform<br>
                Data Revolt Agency</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
Reconciliation Complete - {client_name}

Your transaction reconciliation has been completed successfully.

Match Rate: {match_rate:.1f}% ({status_text})
Missing Transactions: {missing_count}

View full report: {dashboard_url or 'Visit your dashboard'}

Job ID: #{job_id}

---
DRA Transaction Reconciliation Platform
Data Revolt Agency
"""
        
        return await self.send_email(
            to=[EmailRecipient(email=email)],
            subject=f"Reconciliation Complete - {client_name} ({match_rate:.1f}% match)",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_job_failure_notification(
        self,
        email: str,
        client_name: str,
        job_id: int,
        error_message: str,
        dashboard_url: Optional[str] = None
    ) -> dict:
        """Send job failure notification email.
        
        Args:
            email: Recipient email address
            client_name: Name of the client
            job_id: The failed job ID
            error_message: Error message (truncated for email)
            dashboard_url: URL to view details
            
        Returns:
            API response
        """
        # Truncate error message for email
        short_error = error_message[:200] + "..." if len(error_message) > 200 else error_message
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reconciliation Failed - {client_name}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: #dc2626;
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #f9fafb;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .error-box {{
                    background: #fef2f2;
                    border-left: 4px solid #dc2626;
                    padding: 15px;
                    margin: 20px 0;
                    font-family: monospace;
                    font-size: 13px;
                    color: #991b1b;
                }}
                .button {{
                    display: inline-block;
                    background: #dc2626;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: 600;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚠️ Reconciliation Failed</h1>
                <p>{client_name}</p>
            </div>
            <div class="content">
                <p>Your transaction reconciliation job failed to complete.</p>
                
                <div class="error-box">
                    {short_error}
                </div>
                
                <p>This could be due to:</p>
                <ul>
                    <li>Temporary API connectivity issues</li>
                    <li>Expired or invalid API credentials</li>
                    <li>Rate limiting from data sources</li>
                </ul>
                
                <p>The system will automatically retry the job if configured to do so.</p>
                
                <center>
                    <a href="{dashboard_url or '#'}" class="button">
                        View Details
                    </a>
                </center>
                
                <p style="font-size: 14px; color: #6b7280; margin-top: 20px;">
                    Job ID: #{job_id}
                </p>
            </div>
            <div class="footer">
                <p>DRA Transaction Reconciliation Platform<br>
                Data Revolt Agency</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
⚠️ Reconciliation Failed - {client_name}

Your transaction reconciliation job failed to complete.

Error: {short_error}

This could be due to:
- Temporary API connectivity issues
- Expired or invalid API credentials
- Rate limiting from data sources

The system will automatically retry the job if configured to do so.

View details: {dashboard_url or 'Visit your dashboard'}

Job ID: #{job_id}

---
DRA Transaction Reconciliation Platform
Data Revolt Agency
"""
        
        return await self.send_email(
            to=[EmailRecipient(email=email)],
            subject=f"⚠️ Reconciliation Failed - {client_name}",
            html_content=html_content,
            text_content=text_content
        )


class EmailServiceError(Exception):
    """Exception raised when email service fails."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# Global email service instance
email_service = EmailService()
