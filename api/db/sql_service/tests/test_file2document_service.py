import pytest
from datetime import datetime

from api.db.sql_service.services.file2document_service import File2DocumentService
from api.db.sql_service.services.file_service import FileService
from api.db.sql_service.services.document_service import DocumentService
from api.db.sql_service.services.tenant_service import TenantService
from api.db.sql_service.services.user_service import UserService
from api.utils import get_uuid


class TestFile2DocumentService:
    """Test suite for File2DocumentService functionality."""
    
    @pytest.fixture
    def test_user_data(self):
        """Fixture providing test user data."""
        return {
            "id": get_uuid(),
            "email": "test@example.com",
            "password": "test_password",
            "nickname": "Test User",
            "status": "1"
        }
    
    @pytest.fixture
    def test_user(self, test_user_data, db_session):
        """Fixture providing a test user instance."""
        return UserService.save(session=db_session, **test_user_data)
    
    @pytest.fixture
    def test_tenant_data(self):
        """Fixture providing test tenant data."""
        return {
            "id": get_uuid(),
            "name": "Test Tenant",
            "public_key": "test_key",
            "llm_id": "test_llm_id",
            "embd_id": "test_embd_id",
            "asr_id": "test_asr_id",
            "img2txt_id": "test_img2txt_id",
            "rerank_id": "test_rerank_id",
            "tts_id": "test_tts_id",
            "parser_ids": "test_parser_ids",
            "credit": 1000,
            "status": "1"
        }
    
    @pytest.fixture
    def test_tenant(self, test_tenant_data, db_session):
        """Fixture providing a test tenant instance."""
        return TenantService.save(session=db_session, **test_tenant_data)
    
    @pytest.fixture
    def test_association_data(self):
        """Fixture providing test association data."""
        return {
            "file_id": get_uuid(),
            "document_id": get_uuid()
        }
    
    @pytest.fixture
    def test_file_data(self, test_tenant, test_user):
        """Fixture providing test file data."""
        return {
            "id": get_uuid(),
            "parent_id": get_uuid(),
            "tenant_id": test_tenant.id,
            "created_by": test_user.id,  # Use the actual user ID
            "name": "test_file.txt",
            "location": "/test/location",
            "size": 1024,
            "type": "txt",
            "source_type": "local"
        }
    
    @pytest.fixture
    def test_document_data(self, test_user, test_knowledgebase):
        """Fixture providing test document data."""
        return {
            "id": get_uuid(),
            "kb_id": test_knowledgebase.id,
            "parser_id": "naive",
            "source_type": "local",
            "type": "txt",
            "created_by": test_user.id,
            "name": "test_document.txt",
            "location": "/test/location",
            "size": 1024
        }
    
    def test_create_association(self, test_association_data, test_file_data, test_document_data, db_session):
        """Test creating a new file-document association."""
        # Create file and document first
        file = FileService.save(session=db_session, **test_file_data)
        document = DocumentService.save(session=db_session, **test_document_data)
        
        # Update association data with actual IDs
        test_association_data["file_id"] = file.id
        test_association_data["document_id"] = document.id
        
        # Create association
        association = File2DocumentService.save(
            session=db_session,
            **test_association_data
        )
        
        # Verify association was created
        assert association is not None
        assert association.file_id == test_association_data["file_id"]
        assert association.document_id == test_association_data["document_id"]
        
        # Verify timestamps were set
        assert association.create_time is not None
        assert association.create_date is not None
        assert association.update_time is not None
        assert association.update_date is not None
    
    def test_get_associations_by_file(self, test_association_data, test_file_data, test_document_data, db_session):
        """Test retrieving associations by file."""
        # Create file and document first
        file = FileService.save(session=db_session, **test_file_data)
        document = DocumentService.save(session=db_session, **test_document_data)
        
        # Update association data with actual IDs
        test_association_data["file_id"] = file.id
        test_association_data["document_id"] = document.id
        
        # Create association first
        File2DocumentService.save(session=db_session, **test_association_data)
        
        # Retrieve associations by file
        associations = File2DocumentService.get_by_file(
            session=db_session,
            file_id=test_association_data["file_id"]
        )
        
        assert len(associations) == 1
        assert associations[0].document_id == test_association_data["document_id"]
    
    def test_get_associations_by_document(self, test_association_data, test_file_data, test_document_data, db_session):
        """Test retrieving associations by document."""
        # Create file and document first
        file = FileService.save(session=db_session, **test_file_data)
        document = DocumentService.save(session=db_session, **test_document_data)
        
        # Update association data with actual IDs
        test_association_data["file_id"] = file.id
        test_association_data["document_id"] = document.id
        
        # Create association first
        File2DocumentService.save(session=db_session, **test_association_data)
        
        # Retrieve associations by document
        associations = File2DocumentService.get_by_document(
            session=db_session,
            document_id=test_association_data["document_id"]
        )
        
        assert len(associations) == 1
        assert associations[0].file_id == test_association_data["file_id"]
    
    def test_delete_associations_by_file(self, test_association_data, test_file_data, test_document_data, db_session):
        """Test deleting associations by file."""
        # Create file and document first
        file = FileService.save(session=db_session, **test_file_data)
        document = DocumentService.save(session=db_session, **test_document_data)
        
        # Update association data with actual IDs
        test_association_data["file_id"] = file.id
        test_association_data["document_id"] = document.id
        
        # Create association first
        File2DocumentService.save(session=db_session, **test_association_data)
        
        # Delete associations by file
        count = File2DocumentService.delete_by_file(
            session=db_session,
            file_id=test_association_data["file_id"]
        )
        
        # Verify deletion
        assert count == 1
        associations = File2DocumentService.get_by_file(
            session=db_session,
            file_id=test_association_data["file_id"]
        )
        assert len(associations) == 0
    
    def test_delete_associations_by_document(self, test_association_data, test_file_data, test_document_data, db_session):
        """Test deleting associations by document."""
        # Create file and document first
        file = FileService.save(session=db_session, **test_file_data)
        document = DocumentService.save(session=db_session, **test_document_data)
        
        # Update association data with actual IDs
        test_association_data["file_id"] = file.id
        test_association_data["document_id"] = document.id
        
        # Create association first
        File2DocumentService.save(session=db_session, **test_association_data)
        
        # Delete associations by document
        count = File2DocumentService.delete_by_document(
            session=db_session,
            document_id=test_association_data["document_id"]
        )
        
        # Verify deletion
        assert count == 1
        associations = File2DocumentService.get_by_document(
            session=db_session,
            document_id=test_association_data["document_id"]
        )
        assert len(associations) == 0 