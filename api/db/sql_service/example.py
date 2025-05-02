"""Example script for using the SQLAlchemy services.

This script demonstrates how to use the SQLAlchemy implementations
of the RAGFlow services for database operations.
"""

import sys
import os
from datetime import datetime

from api.db.sql_service.database import init_db, session_factory
from api.db.sql_service.services import UserService, TenantService, UserTenantService
from api.db.sql_service.config import DEFAULT_LLM_ID, DEFAULT_EMBEDDING_MODEL_ID
from api.db import UserTenantRole, StatusEnum
from api.utils import get_uuid


def create_user_example():
    """Example of creating a new user."""
    # Create a new user
    user = UserService.save(
        email="example@example.com",
        nickname="Example User",
        password="password123",
        language="English",
        is_superuser=False
    )
    
    print(f"Created user: {user.id}, {user.email}, {user.nickname}")
    return user


def create_tenant_example():
    """Example of creating a new tenant."""
    # Create a new tenant (with model IDs moved to config.py)
    tenant = TenantService.save(
        name="Example Tenant",
        public_key="example-api-key",
        credit=1000
    )
    
    print(f"Created tenant: {tenant.id}, {tenant.name}")
    # Print the default model IDs from config
    print(f"Using default LLM: {DEFAULT_LLM_ID}")
    print(f"Using default embedding model: {DEFAULT_EMBEDDING_MODEL_ID}")
    return tenant


def link_user_tenant_example(user_id, tenant_id):
    """Example of linking a user and tenant."""
    # Create a user-tenant relationship
    user_tenant = UserTenantService.save(
        user_id=user_id,
        tenant_id=tenant_id,
        role=UserTenantRole.OWNER,
        invited_by=user_id,
        status=StatusEnum.VALID.value
    )
    
    print(f"Linked user {user_id} and tenant {tenant_id} with role {user_tenant.role}")
    return user_tenant


def query_user_example(email, password):
    """Example of authenticating a user."""
    # Authenticate user
    user = UserService.query_user(email=email, password=password)
    
    if user:
        print(f"Authentication successful: {user.id}, {user.email}")
    else:
        print("Authentication failed")
    return user


def get_tenant_info_example(user_id):
    """Example of getting tenant information for a user."""
    # Get tenant information
    tenants = TenantService.get_info_by(user_id=user_id)
    
    print(f"Found {len(tenants)} tenants for user {user_id}:")
    for tenant in tenants:
        print(f"  - {tenant['tenant_id']}: {tenant['name']}")
        print(f"    LLM: {tenant['llm_id']}, Embedding: {tenant['embd_id']}")
    return tenants


def update_user_example(user_id):
    """Example of updating a user's information."""
    # Update user
    result = UserService.update_user(
        user_id=user_id, 
        user_dict={
            "nickname": f"Updated User {datetime.now().isoformat()}",
            "language": "Chinese"
        }
    )
    
    print(f"Updated user {user_id}: {result} records affected")
    
    # Get updated user
    success, user = UserService.get_by_id(record_id=user_id)
    if success:
        print(f"Updated user: {user.id}, {user.nickname}, {user.language}")
    
    return user


def main():
    """Run the example script."""
    # Initialize the database schema (this would typically be done at app startup)
    init_db()
    
    # Create a user and tenant, and link them
    user = create_user_example()
    tenant = create_tenant_example()
    user_tenant = link_user_tenant_example(user.id, tenant.id)
    
    # Demonstrate queries
    authenticated_user = query_user_example("example@example.com", "password123")
    tenants = get_tenant_info_example(user.id)
    updated_user = update_user_example(user.id)
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main() 