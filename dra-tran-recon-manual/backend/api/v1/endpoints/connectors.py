from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json

from core.database import get_db
from core.auth import get_current_user, require_admin
from core.encryption import encrypt_config, decrypt_config
from core.rate_limiter import limiter, RateLimits
from models.connector import Connector
from models.client import Client
from schemas.connector import Connector as ConnectorSchema, ConnectorCreate, ConnectorUpdate
from schemas.connector_configs import validate_connector_config, get_connector_schema_example

# Router for nested client routes: /api/v1/clients/{client_id}/connectors
router = APIRouter()

# Router for single connector operations: /api/v1/connectors/{connector_id}
single_router = APIRouter()


@router.post("/", response_model=ConnectorSchema)
@limiter.limit(RateLimits.CREATE)
async def create_connector(
    request: Request,
    client_id: int,
    connector: ConnectorCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """
    Create a new connector for a client.
    
    Validates configuration based on connector type:
    - **ga4**: Requires property_id and credentials_json
    - **shopify**: Requires shop_url and access_token
    - **woocommerce**: Requires url, consumer_key, and consumer_secret
    """
    # Verify client exists
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Validate config based on connector type
    try:
        validated_config = validate_connector_config(connector.type, connector.config)
        # Use the validated model's dict for storage
        config_to_store = validated_config.dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid configuration for {connector.type}: {str(e)}"
        )
    
    # Encrypt the config
    config_json = json.dumps(config_to_store)
    encrypted_config = encrypt_config(config_json)
    
    db_connector = Connector(
        client_id=client_id,
        type=connector.type,
        config_json=encrypted_config
    )
    db.add(db_connector)
    await db.commit()
    await db.refresh(db_connector)
    return db_connector


@router.get("/", response_model=List[ConnectorSchema])
@limiter.limit(RateLimits.LIST)
async def list_connectors(
    request: Request,
    client_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """List all connectors for a client"""
    result = await db.execute(
        select(Connector).where(Connector.client_id == client_id)
    )
    connectors = result.scalars().all()
    return connectors


@single_router.get("/{connector_id}", response_model=ConnectorSchema)
@limiter.limit(RateLimits.GET)
async def get_connector(
    request: Request,
    connector_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get a specific connector"""
    result = await db.execute(
        select(Connector).where(Connector.id == connector_id)
    )
    connector = result.scalars().first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector


@single_router.put("/{connector_id}", response_model=ConnectorSchema)
@limiter.limit(RateLimits.UPDATE)
async def update_connector(
    request: Request,
    connector_id: int,
    connector_update: ConnectorUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Update a connector"""
    result = await db.execute(
        select(Connector).where(Connector.id == connector_id)
    )
    connector = result.scalars().first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    if connector_update.config is not None:
        # Validate config based on connector type (use existing type if not updating)
        connector_type = connector_update.type or connector.type
        try:
            validated_config = validate_connector_config(connector_type, connector_update.config)
            config_to_store = validated_config.dict()
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid configuration for {connector_type}: {str(e)}"
            )
        
        config_json = json.dumps(config_to_store)
        connector.config_json = encrypt_config(config_json)
    
    if connector_update.type is not None:
        connector.type = connector_update.type
    
    await db.commit()
    await db.refresh(connector)
    return connector


@single_router.delete("/{connector_id}")
@limiter.limit(RateLimits.DELETE)
async def delete_connector(
    request: Request,
    connector_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Delete a connector"""
    result = await db.execute(
        select(Connector).where(Connector.id == connector_id)
    )
    connector = result.scalars().first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    await db.delete(connector)
    await db.commit()
    return {"message": "Connector deleted successfully"}


@single_router.post("/{connector_id}/test")
@limiter.limit(RateLimits.CONNECTOR_TEST)
async def test_connector(
    request: Request,
    connector_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Test a connector configuration"""
    result = await db.execute(
        select(Connector).where(Connector.id == connector_id)
    )
    connector = result.scalars().first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    try:
        # Decrypt and parse config
        config_str = decrypt_config(connector.config_json)
        config = json.loads(config_str)
        
        # Test based on type
        if connector.type == "ga4":
            # Import and test GA4
            from core.ingestors.google_analytics import GA4Ingestor
            ingestor = GA4Ingestor(config)
            # Try to fetch just 1 day to test
            df = await ingestor.fetch_data(days=1)
            return {"success": True, "message": f"Connected! Found {len(df)} transactions."}
            
        elif connector.type == "shopify":
            from core.ingestors.shopify import ShopifyIngestor
            ingestor = ShopifyIngestor(config)
            df = await ingestor.fetch_data(days=1)
            return {"success": True, "message": f"Connected! Found {len(df)} orders."}
            
        elif connector.type == "woocommerce":
            from core.ingestors.woocommerce import WooCommerceIngestor
            ingestor = WooCommerceIngestor(config)
            df = await ingestor.fetch_data(days=1)
            return {"success": True, "message": f"Connected! Found {len(df)} orders."}
        else:
            return {"success": False, "message": f"Unknown connector type: {connector.type}"}
            
    except Exception as e:
        return {"success": False, "message": f"Connection failed: {str(e)}"}


@router.get("/config-examples/{connector_type}")
@limiter.limit(RateLimits.GET)
async def get_config_example(
    request: Request,
    connector_type: str,
    user: dict = Depends(require_admin)
):
    """
    Get example configuration for a connector type.
    
    This endpoint returns a sample configuration object that can be used
    when creating or updating a connector of the specified type.
    """
    valid_types = ['ga4', 'shopify', 'woocommerce']
    if connector_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid connector type. Must be one of: {', '.join(valid_types)}"
        )
    
    return {
        "connector_type": connector_type,
        "example_config": get_connector_schema_example(connector_type),
        "description": f"Example configuration for {connector_type} connector"
    }
