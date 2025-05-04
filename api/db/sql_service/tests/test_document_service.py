import pytest
from datetime import datetime

from api.db.sql_service.services.document_service import DocumentService
from api.db import StatusEnum, ParserType
from api.utils import get_uuid


class TestDocumentService:
    """Test suite for DocumentService functionality."""
    
    @pytest.fixture
    def test_document_data(self, test_tenant, test_user, test_knowledgebase):
        """Fixture providing test document data."""
        return {
            "name": "Test Document",
            "kb_id": test_knowledgebase.id,
            "created_by": test_user.id,
            "type": "pdf",
            "status": StatusEnum.VALID.value,
            "parser_id": ParserType.NAIVE.value,
            "parser_config": {"pages": [[1, 1000000]]},
            "source_type": "local"
        }
    
    def test_create_document(self, test_document_data, db_session):
        """Test creating a new document."""
        # Create document
        document = DocumentService.save(
            session=db_session,
            **test_document_data
        )
        
        # Verify document was created
        assert document is not None
        assert document.name == test_document_data["name"]
        assert document.kb_id == test_document_data["kb_id"]
        assert document.type == test_document_data["type"]
        assert document.status == test_document_data["status"]
        
        # Verify default values were set
        assert document.parser_id == test_document_data["parser_id"]
        assert document.source_type == test_document_data["source_type"]
        assert document.progress == 0.0
        assert document.progress_msg == ""
        assert document.run == "0"
        
        # Verify timestamps were set
        assert document.create_time is not None
        assert document.create_date is not None
        assert document.update_time is not None
        assert document.update_date is not None
    
    def test_get_documents_by_knowledgebase(self, test_document_data, db_session):
        """Test retrieving documents by knowledge base."""
        # Create document first
        DocumentService.save(session=db_session, **test_document_data)
        
        # Retrieve documents by knowledge base
        documents = DocumentService.get_by_knowledgebase(
            session=db_session,
            kb_id=test_document_data["kb_id"]
        )
        
        assert len(documents) == 1
        assert documents[0].name == test_document_data["name"]
    
    def test_update_document_progress(self, test_document_data, db_session):
        """Test updating document processing progress."""
        # Create document first
        document = DocumentService.save(
            session=db_session,
            **test_document_data
        )
        
        original_update_time = document.update_time
        
        # Update progress
        process_begin_at = datetime.now().replace(microsecond=0)  # Remove microseconds for consistent comparison
        updated_doc = DocumentService.update_progress(
            session=db_session,
            doc_id=document.id,
            progress=0.5,
            progress_msg="Processing...",
            process_begin_at=process_begin_at
        )
        
        # Verify updates
        assert updated_doc is not None
        assert updated_doc.progress == 0.5
        assert updated_doc.progress_msg == "Processing..."
        assert updated_doc.process_begin_at == process_begin_at
        assert updated_doc.update_time != original_update_time
    
    def test_update_document_processing_status(self, test_document_data, db_session):
        """Test updating document processing status."""
        # Create document first
        document = DocumentService.save(
            session=db_session,
            **test_document_data
        )
        
        original_update_time = document.update_time
        
        # Update processing status
        updated_doc = DocumentService.update_processing_status(
            session=db_session,
            doc_id=document.id,
            run="1"
        )
        
        # Verify updates
        assert updated_doc is not None
        assert updated_doc.run == "1"
        assert updated_doc.update_time != original_update_time 