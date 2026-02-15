"""
Connector Configuration Schemas

Provides strongly-typed validation for each connector type.
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, Dict, Any, Union
import json


class GA4Config(BaseModel):
    """Google Analytics 4 connector configuration"""
    property_id: str = Field(
        ..., 
        description="GA4 Property ID (e.g., '123456789')",
        example="123456789"
    )
    credentials_json: Union[str, Dict[str, Any]] = Field(
        ...,
        description="Service account credentials JSON (string or object)",
        example='{"type": "service_account", "project_id": "..."}'
    )
    
    @validator('credentials_json')
    def validate_credentials(cls, v):
        """Ensure credentials are valid JSON"""
        if isinstance(v, str):
            try:
                data = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("credentials_json must be valid JSON")
        else:
            data = v
        
        # Check required fields for service account
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required credential fields: {', '.join(missing)}")
        
        if data.get('type') != 'service_account':
            raise ValueError("credentials_json must be a service account (type: 'service_account')")
        
        return v
    
    @validator('property_id')
    def validate_property_id(cls, v):
        """Ensure property_id is numeric"""
        if not v.isdigit():
            raise ValueError("property_id must be a numeric string (e.g., '123456789')")
        return v


class ShopifyConfig(BaseModel):
    """Shopify connector configuration"""
    shop_url: str = Field(
        ...,
        description="Shopify store URL (e.g., 'my-store.myshopify.com')",
        example="my-store.myshopify.com"
    )
    access_token: str = Field(
        ...,
        description="Shopify Admin API access token",
        min_length=10,
        example="shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    )
    
    @validator('shop_url')
    def validate_shop_url(cls, v):
        """Normalize and validate shop URL"""
        # Remove protocol if present
        v = v.replace("https://", "").replace("http://", "").rstrip("/")
        
        # Must end with .myshopify.com or be a valid domain
        if not (v.endswith(".myshopify.com") or "." in v):
            raise ValueError("shop_url must be a valid Shopify domain (e.g., 'store.myshopify.com')")
        
        return v
    
    @validator('access_token')
    def validate_access_token(cls, v):
        """Ensure token looks like a Shopify token"""
        if not v.startswith("shpat_") and len(v) < 20:
            raise ValueError("access_token doesn't look like a valid Shopify Admin API token")
        return v


class WooCommerceConfig(BaseModel):
    """WooCommerce connector configuration"""
    url: HttpUrl = Field(
        ...,
        description="WordPress/WooCommerce site URL",
        example="https://my-store.com"
    )
    consumer_key: str = Field(
        ...,
        description="WooCommerce REST API Consumer Key",
        min_length=10,
        example="ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    )
    consumer_secret: str = Field(
        ...,
        description="WooCommerce REST API Consumer Secret",
        min_length=10,
        example="cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    )
    
    @validator('consumer_key')
    def validate_consumer_key(cls, v):
        """Ensure key looks like a WooCommerce key"""
        if not v.startswith("ck_"):
            raise ValueError("consumer_key must start with 'ck_'")
        return v
    
    @validator('consumer_secret')
    def validate_consumer_secret(cls, v):
        """Ensure secret looks like a WooCommerce secret"""
        if not v.startswith("cs_"):
            raise ValueError("consumer_secret must start with 'cs_'")
        return v


# Union type for all connector configs
ConnectorConfigType = Union[GA4Config, ShopifyConfig, WooCommerceConfig]


def validate_connector_config(connector_type: str, config: Dict[str, Any]) -> ConnectorConfigType:
    """
    Validate connector configuration based on type.
    
    Args:
        connector_type: One of 'ga4', 'shopify', 'woocommerce'
        config: Configuration dictionary
        
    Returns:
        Validated config model
        
    Raises:
        ValueError: If config is invalid for the connector type
    """
    validators = {
        'ga4': GA4Config,
        'shopify': ShopifyConfig,
        'woocommerce': WooCommerceConfig
    }
    
    if connector_type not in validators:
        raise ValueError(f"Unknown connector type: {connector_type}. Must be one of: {', '.join(validators.keys())}")
    
    return validators[connector_type](**config)


def get_connector_schema_example(connector_type: str) -> Dict[str, Any]:
    """Get example configuration for a connector type"""
    examples = {
        'ga4': {
            "property_id": "123456789",
            "credentials_json": {
                "type": "service_account",
                "project_id": "my-project",
                "private_key_id": "...",
                "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
                "client_email": "analytics@my-project.iam.gserviceaccount.com",
                "client_id": "...",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        'shopify': {
            "shop_url": "my-store.myshopify.com",
            "access_token": "shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        },
        'woocommerce': {
            "url": "https://my-store.com",
            "consumer_key": "ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "consumer_secret": "cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        }
    }
    
    return examples.get(connector_type, {})
