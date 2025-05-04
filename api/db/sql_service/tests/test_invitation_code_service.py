import pytest
from datetime import datetime
import time

from api.db.sql_service.services.invitation_code_service import InvitationCodeService
from api.db import StatusEnum
from api.utils import get_uuid


class TestInvitationCodeService:
    """Test suite for InvitationCodeService functionality."""
    
    @pytest.fixture
    def test_invitation_code_data(self, test_tenant):
        """Fixture providing test invitation code data."""
        return {
            "code": "TEST123",
            "tenant_id": test_tenant.id,
            "status": StatusEnum.VALID.value
        }
    
    def test_create_invitation_code(self, test_invitation_code_data, db_session):
        """Test creating a new invitation code."""
        # Create invitation code
        invitation_code = InvitationCodeService.save(
            session=db_session,
            **test_invitation_code_data
        )
        
        # Verify invitation code was created
        assert invitation_code is not None
        assert invitation_code.code == test_invitation_code_data["code"]
        assert invitation_code.tenant_id == test_invitation_code_data["tenant_id"]
        assert invitation_code.status == test_invitation_code_data["status"]
        
        # Verify timestamps were set
        assert invitation_code.create_time is not None
        assert invitation_code.create_date is not None
        assert invitation_code.update_time is not None
        assert invitation_code.update_date is not None
    
    def test_get_invitation_code_by_code(self, test_invitation_code_data, db_session):
        """Test retrieving invitation code by code value."""
        # Create invitation code first
        InvitationCodeService.save(session=db_session, **test_invitation_code_data)
        
        # Retrieve invitation code by code
        invitation_code = InvitationCodeService.get_by_code(
            session=db_session,
            code=test_invitation_code_data["code"]
        )
        
        assert invitation_code is not None
        assert invitation_code.code == test_invitation_code_data["code"]
        assert invitation_code.tenant_id == test_invitation_code_data["tenant_id"]
    
    def test_mark_invitation_code_as_used(self, test_invitation_code_data, db_session):
        """Test marking an invitation code as used."""
        # Create invitation code first
        invitation_code = InvitationCodeService.save(
            session=db_session,
            **test_invitation_code_data
        )
        
        # Store original update time
        original_update_time = invitation_code.update_time
        
        # Add a small delay to ensure different timestamps
        time.sleep(0.001)  # 1 millisecond delay
        
        # Mark as used
        user_id = get_uuid()
        updated_code = InvitationCodeService.mark_as_used(
            session=db_session,
            code_id=invitation_code.id,
            user_id=user_id
        )
        
        # Verify updates
        assert updated_code is not None
        assert updated_code.user_id == user_id
        assert updated_code.status == StatusEnum.INVALID.value
        assert updated_code.visit_time is not None
        assert updated_code.update_time > original_update_time  # Compare with stored original time 