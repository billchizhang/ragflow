import pytest
from datetime import datetime
import time

from api.db.sql_service.services.user_service import UserService
from api.db import StatusEnum
from api.utils import get_uuid


class TestUserService:
    """Test suite for UserService functionality."""
    
    @pytest.fixture
    def test_user_data(self):
        """Fixture providing test user data."""
        return {
            "email": "test@example.com",
            "password": "test_password",
            "nickname": "Test User",
            "is_authenticated": True,
            "is_active": True,
            "is_anonymous": False,
            "status": StatusEnum.VALID.value,
            "is_superuser": False
        }
    
    def test_create_user(self, test_user_data, db_session):
        """Test creating a new user."""
        # Create user
        user = UserService.save(session=db_session, **test_user_data)
        
        # Verify user was created
        assert user is not None
        assert user.email == test_user_data["email"]
        assert user.nickname == test_user_data["nickname"]
        assert user.is_active == test_user_data["is_active"]
        assert user.is_authenticated == test_user_data["is_authenticated"]
        assert user.status == test_user_data["status"]
    
    def test_authenticate_user(self, test_user_data, db_session):
        """Test user authentication."""
        # Create user first
        UserService.save(session=db_session, **test_user_data)
        
        # Test successful authentication
        user = UserService.query_user(
            session=db_session,
            email=test_user_data["email"],
            password=test_user_data["password"]
        )
        assert user is not None
        assert user.email == test_user_data["email"]
        
        # Test failed authentication
        user = UserService.query_user(
            session=db_session,
            email=test_user_data["email"],
            password="wrong_password"
        )
        assert user is None
    
    def test_get_user_by_id(self, test_user_data, db_session):
        """Test retrieving user by ID."""
        # Create user first
        user = UserService.save(session=db_session, **test_user_data)
        
        # Retrieve user by ID
        retrieved_user = UserService.filter_by_id(session=db_session, user_id=user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.email == user.email
    
    def test_update_user(self, test_user_data, db_session):
        """Test updating user information."""
        # Create user first
        user = UserService.save(session=db_session, **test_user_data)
        
        # Store original values
        original_nickname = user.nickname
        original_email = user.email
        
        # Update user
        update_data = {
            "nickname": "Updated Name",
            "email": "updated@example.com"
        }
        updated_user = UserService.update_user(
            session=db_session,
            user_id=user.id,
            user_dict=update_data
        )
        
        # Verify updates
        assert updated_user is not None
        assert updated_user.nickname == update_data["nickname"]
        assert updated_user.email == update_data["email"]
        assert updated_user.nickname != original_nickname
        assert updated_user.email != original_email
    
    def test_delete_user(self, test_user_data, db_session):
        """Test deleting a user."""
        # Create user first
        user = UserService.save(session=db_session, **test_user_data)
        
        # Delete user
        update_data = {"status": StatusEnum.DELETED.value}
        UserService.delete_user(
            session=db_session,
            user_ids=[user.id],
            update_user_dict=update_data
        )
        
        # Verify user was deleted
        deleted_user = UserService.filter_by_id(session=db_session, user_id=user.id)
        assert deleted_user is not None
        assert deleted_user.status == StatusEnum.DELETED.value 