import pytest
from datetime import datetime

from api.db.sql_service.services.user_service import UserService
from api.db.sql_service.services.tenant_service import TenantService
from api.db.sql_service.services.user_tenant_service import UserTenantService
from api.db import StatusEnum, UserTenantRole
from api.utils import get_uuid


class TestUserTenantService:
    """Test suite for UserTenantService functionality."""
    
    @pytest.fixture
    def test_user_data(self):
        """Fixture providing test user data."""
        return {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User",
            "status": StatusEnum.VALID.value,
            "is_authenticated": True,
            "is_active": True
        }
    
    @pytest.fixture
    def test_tenant_data(self):
        """Fixture providing test tenant data."""
        return {
            "name": "Test Tenant",
            "public_key": "test_public_key",
            "llm_id": "test_llm_id",
            "embd_id": "test_embd_id",
            "asr_id": "test_asr_id",
            "img2txt_id": "test_img2txt_id",
            "rerank_id": "test_rerank_id",
            "tts_id": "test_tts_id",
            "parser_ids": "test_parser_ids",
            "credit": 1000,
            "status": StatusEnum.VALID.value
        }
    
    def test_create_user_tenant_relationship(self, test_user_data, test_tenant_data, db_session):
        """Test creating a user-tenant relationship."""
        # Create user and tenant first
        user = UserService.save(session=db_session, **test_user_data)
        tenant = TenantService.save(session=db_session, **test_tenant_data)
        
        # Create relationship
        relationship_data = {
            "user_id": user.id,
            "tenant_id": tenant.id,
            "role": UserTenantRole.OWNER.value,
            "invited_by": user.id  # User is inviting themselves
        }
        relationship = UserTenantService.save(session=db_session, **relationship_data)
        
        # Verify relationship was created
        assert relationship is not None
        assert relationship.user_id == user.id
        assert relationship.tenant_id == tenant.id
        assert relationship.role == UserTenantRole.OWNER.value
    
    def test_get_tenants_by_user_id(self, test_user_data, test_tenant_data, db_session):
        """Test getting tenants associated with a user."""
        # Create user and tenant first
        user = UserService.save(session=db_session, **test_user_data)
        tenant = TenantService.save(session=db_session, **test_tenant_data)
        
        # Create relationship
        UserTenantService.save(
            session=db_session,
            user_id=user.id,
            tenant_id=tenant.id,
            role=UserTenantRole.OWNER.value,
            invited_by=user.id  # User is inviting themselves
        )
        
        # Get tenants for user
        tenants = UserTenantService.get_tenants_by_user_id(session=db_session, user_id=user.id)
        
        # Verify tenants were retrieved
        assert tenants is not None
        assert len(tenants) == 1
        assert tenants[0].id == tenant.id
    
    def test_get_users_by_tenant_id(self, test_user_data, test_tenant_data, db_session):
        """Test getting users associated with a tenant."""
        # Create user and tenant first
        user = UserService.save(session=db_session, **test_user_data)
        tenant = TenantService.save(session=db_session, **test_tenant_data)
        
        # Create relationship
        UserTenantService.save(
            session=db_session,
            user_id=user.id,
            tenant_id=tenant.id,
            role=UserTenantRole.OWNER.value,
            invited_by=user.id  # User is inviting themselves
        )
        
        # Get users for tenant
        users = UserTenantService.get_users_by_tenant_id(session=db_session, tenant_id=tenant.id)
        
        # Verify users were retrieved
        assert users is not None
        assert len(users) == 1
        assert users[0].id == user.id
    
    def test_update_user_tenant_role(self, test_user_data, test_tenant_data, db_session):
        """Test updating a user's role in a tenant."""
        # Create user and tenant first
        user = UserService.save(session=db_session, **test_user_data)
        tenant = TenantService.save(session=db_session, **test_tenant_data)
        
        # Create initial relationship
        relationship = UserTenantService.save(
            session=db_session,
            user_id=user.id,
            tenant_id=tenant.id,
            role=UserTenantRole.OWNER.value,
            invited_by=user.id  # User is inviting themselves
        )
        
        # Update role
        new_role = UserTenantRole.NORMAL.value
        updated_relationship = UserTenantService.update_by_id(
            session=db_session,
            record_id=relationship.id,
            data={"role": new_role}
        )
        
        # Verify role was updated
        assert updated_relationship is not None
        assert updated_relationship.role == new_role 