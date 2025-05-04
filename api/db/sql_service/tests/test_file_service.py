import pytest
from datetime import datetime
import time

from api.db.sql_service.services.file_service import FileService
from api.utils import get_uuid


class TestFileService:
    """Test suite for FileService functionality."""
    
    @pytest.fixture
    def test_file_data(self, test_tenant, test_user):
        """Fixture providing test file data."""
        return {
            "name": "test_file.pdf",
            "parent_id": get_uuid(),
            "tenant_id": test_tenant.id,
            "created_by": test_user.id,
            "type": "pdf",
            "size": 1024
        }
    
    def test_create_file(self, test_file_data, db_session):
        """Test creating a new file."""
        # Create file
        file = FileService.save(
            session=db_session,
            **test_file_data
        )
        
        # Verify file was created
        assert file is not None
        assert file.name == test_file_data["name"]
        assert file.parent_id == test_file_data["parent_id"]
        assert file.tenant_id == test_file_data["tenant_id"]
        assert file.type == test_file_data["type"]
        assert file.size == test_file_data["size"]
        
        # Verify default values were set
        assert file.source_type == ""
        
        # Verify timestamps were set
        assert file.create_time is not None
        assert file.create_date is not None
        assert file.update_time is not None
        assert file.update_date is not None
    
    def test_get_files_by_tenant(self, test_file_data, db_session):
        """Test retrieving files by tenant."""
        # Create file first
        FileService.save(session=db_session, **test_file_data)
        
        # Retrieve files by tenant
        files = FileService.get_by_tenant(
            session=db_session,
            tenant_id=test_file_data["tenant_id"]
        )
        
        assert len(files) == 1
        assert files[0].name == test_file_data["name"]
    
    def test_get_files_by_parent(self, test_file_data, db_session):
        """Test retrieving files by parent directory."""
        # Create file first
        FileService.save(session=db_session, **test_file_data)
        
        # Retrieve files by parent
        files = FileService.get_by_parent(
            session=db_session,
            parent_id=test_file_data["parent_id"]
        )
        
        assert len(files) == 1
        assert files[0].name == test_file_data["name"]
    
    def test_update_file_location(self, test_file_data, db_session):
        """Test updating file location."""
        # Create file first
        file = FileService.save(
            session=db_session,
            **test_file_data
        )
        
        # Store original update time
        original_update_time = file.update_time
        
        # Add a small delay to ensure different timestamps
        time.sleep(0.001)
        
        # Update location
        new_location = "/new/path/to/file.pdf"
        updated_file = FileService.update_location(
            session=db_session,
            file_id=file.id,
            location=new_location
        )
        
        # Verify updates
        assert updated_file is not None
        assert updated_file.location == new_location
        assert updated_file.update_time != original_update_time 