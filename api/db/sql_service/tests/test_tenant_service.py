import pytest
from datetime import datetime
import time

from api.db.sql_service.services.tenant_service import TenantService
from api.db.sql_service.models.models import Tenant
from api.db import StatusEnum
from api.utils import get_uuid
from api.db.sql_service.services.user_service import UserService
from api.db.sql_service.models.models import UserTenant, UserTenantRole
from api.db.sql_service.services.user_tenant_service import UserTenantService


class TestTenantService:
    """Test suite for TenantService functionality."""
    
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
    
    def test_create_tenant(self, test_tenant_data, db_session):
        """Test creating a new tenant."""
        # Create tenant
        tenant = TenantService.save(session=db_session, **test_tenant_data)
        
        # Verify tenant was created
        assert tenant is not None
        assert tenant.name == test_tenant_data["name"]
        assert tenant.public_key == test_tenant_data["public_key"]
        assert tenant.credit == test_tenant_data["credit"]
        assert tenant.status == test_tenant_data["status"]
        
        # Verify timestamps were set
        assert tenant.create_time is not None
        assert tenant.create_date is not None
        assert tenant.update_time is not None
        assert tenant.update_date is not None
    
    def test_get_tenant_by_id(self, test_tenant_data, db_session):
        """Test retrieving tenant by ID."""
        # Create tenant first
        tenant = TenantService.save(session=db_session, **test_tenant_data)
        
        # Retrieve tenant by ID
        retrieved_tenant = TenantService.get_by_id(session=db_session, record_id=tenant.id)
        assert retrieved_tenant is not None
        assert retrieved_tenant.id == tenant.id
        assert retrieved_tenant.name == tenant.name
    
    def test_update_tenant(self, test_tenant_data, db_session):
        """Test updating tenant information."""
        # Create tenant first
        tenant = TenantService.save(session=db_session, **test_tenant_data)
        
        # Store original values
        original_name = tenant.name
        original_credit = tenant.credit
        
        # Update tenant
        update_data = {
            "name": "Updated Tenant",
            "credit": 2000
        }
        updated_tenant = TenantService.update_by_id(
            session=db_session,
            record_id=tenant.id,
            data=update_data
        )
        
        # Verify updates
        assert updated_tenant is not None
        assert updated_tenant.name == update_data["name"]
        assert updated_tenant.credit == update_data["credit"]
        assert updated_tenant.name != original_name
        assert updated_tenant.credit != original_credit
    
    def test_decrease_credit(self, test_tenant_data, db_session):
        """Test decreasing tenant credit."""
        # Create tenant first
        tenant = TenantService.save(session=db_session, **test_tenant_data)
        
        # Decrease credit
        amount = 500
        TenantService.decrease(
            session=db_session,
            tenant_id=tenant.id,
            num=amount
        )
        
        # Verify credit was decreased
        updated_tenant = TenantService.get_by_id(session=db_session, record_id=tenant.id)
        assert updated_tenant.credit == test_tenant_data["credit"] - amount
    
    def test_get_tenant_info(self, test_tenant_data, test_user_data, db_session):
        """Test getting tenant information."""
        # Create user and tenant first
        user = UserService.save(session=db_session, **test_user_data)
        tenant = TenantService.save(session=db_session, **test_tenant_data)
        
        # Create user-tenant relationship
        UserTenantService.save(
            session=db_session,
            user_id=user.id,
            tenant_id=tenant.id,
            role=UserTenantRole.OWNER.value,
            invited_by=user.id  # User is inviting themselves
        )
        
        # Get tenant info
        tenant_info = TenantService.get_info_by(session=db_session, user_id=user.id)
        assert tenant_info is not None
        assert tenant_info.id == tenant.id
        assert tenant_info.name == tenant.name 