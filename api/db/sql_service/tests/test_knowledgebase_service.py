import pytest
from datetime import datetime

from api.db.sql_service.services.knowledgebase_service import KnowledgebaseService
from api.db.sql_service.models.models import Document
from api.db import StatusEnum, ParserType, TenantPermission
from api.utils import get_uuid


class TestKnowledgebaseService:
    """Test suite for KnowledgebaseService functionality."""
    
    @pytest.fixture
    def test_knowledgebase_data(self, test_tenant, test_user):
        """Fixture providing test knowledge base data."""
        return {
            "name": "Test Knowledge Base",
            "tenant_id": test_tenant.id,
            "embd_id": "test_embd_id",
            "created_by": test_user.id,
            "status": StatusEnum.VALID.value
        }
    
    def test_create_knowledgebase(self, test_knowledgebase_data, db_session):
        """Test creating a new knowledge base."""
        # Create knowledge base
        knowledgebase = KnowledgebaseService.save(
            session=db_session,
            **test_knowledgebase_data
        )
        
        # Verify knowledge base was created
        assert knowledgebase is not None
        assert knowledgebase.name == test_knowledgebase_data["name"]
        assert knowledgebase.tenant_id == test_knowledgebase_data["tenant_id"]
        assert knowledgebase.embd_id == test_knowledgebase_data["embd_id"]
        assert knowledgebase.status == test_knowledgebase_data["status"]
        
        # Verify default values were set
        assert knowledgebase.parser_id == ParserType.NAIVE.value
        assert knowledgebase.permission == TenantPermission.ME.value
        assert knowledgebase.similarity_threshold == 0.2
        assert knowledgebase.vector_similarity_weight == 0.3
        
        # Verify timestamps were set
        assert knowledgebase.create_time is not None
        assert knowledgebase.create_date is not None
        assert knowledgebase.update_time is not None
        assert knowledgebase.update_date is not None
    
    def test_get_knowledgebases_by_tenant(self, test_knowledgebase_data, db_session):
        """Test retrieving knowledge bases by tenant."""
        # Create knowledge base first
        KnowledgebaseService.save(session=db_session, **test_knowledgebase_data)
        
        # Retrieve knowledge bases by tenant
        knowledgebases = KnowledgebaseService.get_by_tenant(
            session=db_session,
            tenant_id=test_knowledgebase_data["tenant_id"]
        )
        
        assert len(knowledgebases) == 1
        assert knowledgebases[0].name == test_knowledgebase_data["name"]
    
    def test_get_knowledgebase_with_documents(self, test_knowledgebase_data, db_session):
        """Test retrieving a knowledge base with its documents."""
        # Create knowledge base first
        knowledgebase = KnowledgebaseService.save(
            session=db_session,
            **test_knowledgebase_data
        )
        
        # Create test document
        document = Document(
            id=get_uuid(),
            kb_id=knowledgebase.id,
            name="Test Document",
            status=StatusEnum.VALID.value,
            parser_id=ParserType.NAIVE.value,
            parser_config={"pages": [[1, 1000000]]},
            source_type="local",
            type="text",
            created_by=test_knowledgebase_data["created_by"]
        )
        db_session.add(document)
        db_session.flush()
        
        # Retrieve knowledge base with documents
        kb_with_docs = KnowledgebaseService.get_with_documents(
            session=db_session,
            kb_id=knowledgebase.id
        )
        
        assert kb_with_docs is not None
        assert len(kb_with_docs.documents) == 1
        assert kb_with_docs.documents[0].name == "Test Document"
    
    def test_update_knowledgebase_stats(self, test_knowledgebase_data, db_session):
        """Test updating knowledge base statistics."""
        # Create knowledge base first
        knowledgebase = KnowledgebaseService.save(
            session=db_session,
            **test_knowledgebase_data
        )
        
        # Store original update time
        original_update_time = knowledgebase.update_time
        
        # Update stats
        updated_kb = KnowledgebaseService.update_stats(
            session=db_session,
            kb_id=knowledgebase.id,
            doc_num=10,
            token_num=1000,
            chunk_num=100
        )
        
        # Verify updates
        assert updated_kb is not None
        assert updated_kb.doc_num == 10
        assert updated_kb.token_num == 1000
        assert updated_kb.chunk_num == 100
        assert updated_kb.update_time != original_update_time, "Update time should change after update" 