# Production Deployment Guide

> **Last Updated**: 2026-02-17  
> **Version**: 2.0.0

This guide covers deploying the DRA Transaction Reconciliation Platform to production.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Backend Deployment](#backend-deployment)
6. [Frontend Deployment](#frontend-deployment)
7. [Post-Deployment Verification](#post-deployment-verification)
8. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### Required Services

| Service | Purpose | Recommended Provider |
|---------|---------|---------------------|
| PostgreSQL | Database | Supabase, AWS RDS, or self-hosted |
| Redis | Caching & Scheduler | Redis Cloud, Upstash, or self-hosted |
| Email Service | Notifications | Resend (free tier: 100/day) |
| Error Tracking | Monitoring | Sentry (free tier) |
| Hosting | Application | Railway, Render, AWS, or VPS |

### Required Accounts

- [ ] Supabase account (for auth + database)
- [ ] Resend account (for email)
- [ ] Sentry account (for error tracking)
- [ ] Domain name (for production)
- [ ] SSL certificate (Let's Encrypt is free)

---

## Infrastructure Setup

### Option 1: Railway (Recommended for simplicity)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd dra-tran-recon-manual/backend
railway init

# Add PostgreSQL plugin
railway add --plugin postgresql

# Add Redis plugin
railway add --plugin redis

# Deploy
railway up
```

### Option 2: Render

1. Create a new Web Service
2. Connect your GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main.py`
5. Add environment variables (see below)
6. Create PostgreSQL database
7. Create Redis instance

### Option 3: AWS (EC2 + RDS + ElastiCache)

More complex but cost-effective at scale:

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier dra-platform \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --allocated-storage 20

# Create ElastiCache Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id dra-redis \
  --cache-node-type cache.t3.micro \
  --engine redis

# Deploy to EC2 or ECS
```

---

## Environment Configuration

Create a `.env` file for production:

```bash
# ============================================
# Production Environment Configuration
# ============================================

# Application
ENVIRONMENT=production
VERSION=2.0.0
LOG_LEVEL=INFO

# Database (from your provider)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Security (generate new key for production)
ENCRYPTION_KEY=your-production-fernet-key

# Supabase (production project)
SUPABASE_URL=https://your-production-project.supabase.co
SUPABASE_ANON_KEY=your-production-anon-key
SUPABASE_JWT_SECRET=your-production-jwt-secret

# Frontend (your production domain)
FRONTEND_URL=https://app.yourdomain.com
CORS_ORIGINS=https://app.yourdomain.com,https://admin.yourdomain.com

# Email (Resend production key)
RESEND_API_KEY=re_your_production_key
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME="Your Company Name"

# Redis (for production persistence)
REDIS_URL=redis://your-redis-host:6379/0
CACHE_ENABLED=true

# Sentry (error tracking)
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# Webhooks (generate secure random string)
WEBHOOK_SECRET=your-secure-random-secret-min-32-chars
```

### Generating Secure Keys

```bash
# Encryption key (Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Webhook secret
openssl rand -base64 32
```

---

## Database Setup

### 1. Run Migrations

```bash
cd dra-tran-recon-manual/backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# If no migrations exist yet, create schema
psql $DATABASE_URL < database/COMPLETE_SETUP.sql
```

### 2. Create Admin User

```bash
# Via Supabase Dashboard:
# 1. Go to Authentication → Users
# 2. Click "Add User"
# 3. Enter admin email (must match admin pattern: @yourdomain.com)
# 4. Set password
# 5. Confirm email

# Via API:
curl -X POST "https://your-project.supabase.co/auth/v1/admin/users" \
  -H "Authorization: Bearer $SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourdomain.com",
    "password": "SecurePassword123!",
    "email_confirm": true
  }'
```

### 3. Verify Database Tables

```sql
-- Check all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Expected: clients, connectors, jobs, schedules, user_clients, etc.
```

---

## Backend Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations and start
CMD alembic upgrade head && python main.py
```

```bash
# Build and push
docker build -t dra-platform:latest .
docker tag dra-platform:latest your-registry/dra-platform:latest
docker push your-registry/dra-platform:latest
```

### Environment-Specific Settings

**Development**:
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Production**:
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://app.yourdomain.com
SENTRY_DSN=https://...  # Enable error tracking
REDIS_URL=redis://...   # Enable persistence
```

---

## Frontend Deployment

### Vercel (Recommended)

```bash
cd dra-tran-recon-manual/frontend

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod

# Set environment variables in Vercel dashboard:
# NEXT_PUBLIC_SUPABASE_URL
# NEXT_PUBLIC_SUPABASE_ANON_KEY
# NEXT_PUBLIC_API_URL (your backend URL)
```

### Netlify

```bash
# Build locally
npm run build

# Deploy to Netlify
netlify deploy --prod --dir=out
```

### Environment Variables

Create `.env.local` for production:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-production-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-production-anon-key
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## Post-Deployment Verification

### 1. Health Check

```bash
# Backend health
curl https://api.yourdomain.com/health

# Expected response:
{
  "status": "healthy",
  "checks": {
    "api": "pass",
    "database": "pass"
  }
}
```

### 2. API Documentation

```bash
# View API docs (development only)
open https://api.yourdomain.com/docs
```

### 3. End-to-End Test

1. **Login**: Access `https://app.yourdomain.com/login`
2. **Create Client**: Admin panel → Clients → Create
3. **Add Connectors**: Add test Shopify/GA4 connectors
4. **Run Job**: Trigger reconciliation job
5. **View Results**: Check results page loads correctly

### 4. Email Test

```bash
# Test email delivery
curl -X POST "https://api.yourdomain.com/api/v1/clients/1/invite" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "role": "viewer"}'
```

Check Resend dashboard for delivery status.

### 5. Error Tracking Verification

```python
# Trigger a test error in Python shell
from core.monitoring import capture_message
capture_message("Production deployment test", level="info")
```

Check Sentry dashboard for the test event.

---

## Monitoring & Maintenance

### Health Monitoring

Set up uptime monitoring:

```bash
# Using UptimeRobot (free tier)
# Add monitor for: https://api.yourdomain.com/health
# Check interval: 5 minutes
# Alert email: your-email@domain.com
```

### Log Aggregation

For production, send logs to a centralized service:

```bash
# Option 1: Datadog
pip install datadog

# Option 2: Logtail
pip install logtail-python

# Option 3: CloudWatch (AWS)
# Configure via AWS console
```

### Backup Verification

Test backup restoration monthly:

```bash
# Download latest backup
aws s3 cp s3://your-backup-bucket/latest.dump ./test-restore.dump

# Restore to test database
createdb dra_test
pg_restore --dbname=dra_test test-restore.dump

# Verify
cd dra-tran-recon-manual/backend
DATABASE_URL=postgresql://localhost/dra_test python -c "
import asyncio
from core.database import engine
async def test():
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT COUNT(*) FROM clients'))
        print(f'Clients: {result.scalar()}')
asyncio.run(test())
"

# Cleanup
dropdb dra_test
rm test-restore.dump
```

### Performance Monitoring

Monitor these metrics:

| Metric | Warning Threshold | Critical Threshold |
|--------|------------------|-------------------|
| Response Time | > 500ms | > 2s |
| Error Rate | > 1% | > 5% |
| Database CPU | > 70% | > 90% |
| Disk Usage | > 70% | > 85% |

### Security Checklist

- [ ] SSL certificate installed and valid
- [ ] Environment variables not exposed in logs
- [ ] API rate limiting enabled
- [ ] CORS restricted to known origins
- [ ] Database credentials rotated
- [ ] Encryption key backed up securely
- [ ] Admin passwords are strong
- [ ] 2FA enabled on all service accounts

---

## Troubleshooting

### Common Issues

**Database Connection Failed**:
```bash
# Check connection string format
# Must use asyncpg driver: postgresql+asyncpg://
# Verify firewall rules allow connection
```

**CORS Errors**:
```bash
# Verify CORS_ORIGINS includes your frontend URL
# Check for trailing slashes (shouldn't have them)
```

**Scheduler Not Running**:
```bash
# Check Redis connection
# Verify only one instance is running scheduler
# Check logs for startup errors
```

**Emails Not Sending**:
```bash
# Verify RESEND_API_KEY is set
# Check Resend dashboard for delivery status
# Verify FROM_EMAIL domain is verified in Resend
```

---

## Rollback Procedures

### Database Rollback

```bash
# Restore from backup
pg_restore --clean --if-exists --dbname=$DATABASE_URL backup_file.dump

# Or using psql for SQL dumps
psql $DATABASE_URL < backup_file.sql
```

### Application Rollback

```bash
# Docker
docker pull your-registry/dra-platform:previous-version
docker stop dra-platform
docker run -d --name dra-platform your-registry/dra-platform:previous-version

# Railway
railway up --service dra-platform

# Render
# Use Render dashboard to rollback to previous deployment
```

---

## Support

For deployment support:
- **Email**: devops@datarevolt.agency
- **Slack**: #deployment-support
- **Documentation**: https://docs.datarevolt.agency

---

## Related Documents

- [BACKUP_STRATEGY.md](database/BACKUP_STRATEGY.md)
- [DATA_RETENTION.md](database/DATA_RETENTION.md)
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md)
- [API_MAP.md](docs/API_MAP.md)
