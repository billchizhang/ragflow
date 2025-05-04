import pytest
from datetime import datetime
import time

from api.db.sql_service.services.conversation_service import ConversationService
from api.db.sql_service.services.tenant_service import TenantService
from api.db.sql_service.services.dialog_service import DialogService
from api.db.sql_service.services.user_service import UserService
from api.db.sql_service.models.models import Conversation
from api.db import StatusEnum
from api.utils import get_uuid


class TestConversationService:
    @pytest.fixture
    def test_user_data(self):
        """Fixture providing test user data."""
        return {
            "email": "test@example.com",
            "nickname": "Test User",
            "password": "test_password",
            "is_authenticated": True,
            "is_active": True,
            "is_anonymous": False,
            "status": StatusEnum.VALID.value,
            "is_superuser": False
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

    @pytest.fixture
    def test_dialog_data(self, test_tenant_data, db_session):
        """Fixture providing test dialog data."""
        # Create tenant first
        tenant = TenantService.save(session=db_session, **test_tenant_data)
        
        dialog_data = {
            "tenant_id": tenant.id,
            "name": "Test Dialog",
            "description": "Test dialog description",
            "prompt_type": "simple",
            "prompt_config": {
                "system": "Test system prompt",
                "prologue": "Test prologue",
                "parameters": [],
                "empty_response": "Test empty response"
            },
            "llm_setting": {
                "temperature": 0.1,
                "top_p": 0.3,
                "frequency_penalty": 0.7,
                "presence_penalty": 0.4,
                "max_tokens": 512
            },
            "similarity_threshold": 0.2,
            "vector_similarity_weight": 0.3,
            "top_n": 6,
            "top_k": 1024,
            "do_refer": "1",
            "kb_ids": [],
            "llm_id": "test_llm_id",
            "rerank_id": "test_rerank_id"
        }
        
        # Create dialog
        dialog = DialogService.save(session=db_session, **dialog_data)
        return dialog

    @pytest.fixture
    def test_conversation_data(self, test_dialog_data, test_user_data, db_session):
        """Fixture to provide test data for conversation creation."""
        # Create test user first
        user = UserService.save(session=db_session, **test_user_data)
        
        return {
            "dialog_id": test_dialog_data.id,
            "name": "Test Conversation",
            "message": [{"role": "user", "content": "Hello"}],
            "reference": [],
            "user_id": user.id
        }

    def test_create_conversation(self, test_conversation_data, db_session):
        """Test creating a new conversation."""
        conversation = ConversationService.save(session=db_session, **test_conversation_data)
        assert conversation is not None
        assert conversation.id is not None
        assert conversation.dialog_id == test_conversation_data["dialog_id"]
        assert conversation.name == test_conversation_data["name"]
        assert conversation.message == test_conversation_data["message"]
        assert conversation.reference == test_conversation_data["reference"]
        assert conversation.user_id == test_conversation_data["user_id"]
        assert conversation.create_time is not None
        assert conversation.update_time is not None

    def test_get_by_dialog(self, test_conversation_data, db_session):
        """Test retrieving conversations by dialog ID."""
        # Create multiple conversations
        conversation1 = ConversationService.save(session=db_session, **test_conversation_data)
        test_conversation_data["name"] = "Test Conversation 2"
        conversation2 = ConversationService.save(session=db_session, **test_conversation_data)

        # Get conversations by dialog ID
        conversations = ConversationService.get_by_dialog(session=db_session, dialog_id=test_conversation_data["dialog_id"])
        assert len(conversations) == 2
        assert conversations[0].id in [conversation1.id, conversation2.id]
        assert conversations[1].id in [conversation1.id, conversation2.id]

    def test_update_message(self, test_conversation_data, db_session):
        """Test updating a conversation's message."""
        # Create conversation first
        conversation = ConversationService.save(session=db_session, **test_conversation_data)
        
        # Update message
        new_message = [{"role": "assistant", "content": "Hi there!"}]
        updated_conversation = ConversationService.update_message(
            session=db_session,
            conversation_id=conversation.id,
            message=new_message
        )
        
        assert updated_conversation is not None
        assert updated_conversation.message == new_message
        
        # Verify the update was persisted
        reloaded_conversation = db_session.query(Conversation).filter(
            Conversation.id == conversation.id
        ).first()
        assert reloaded_conversation.message == new_message

    def test_update_reference(self, test_conversation_data, db_session):
        """Test updating a conversation's reference."""
        # Create conversation first
        conversation = ConversationService.save(session=db_session, **test_conversation_data)
        
        # Update reference
        new_reference = [{"doc_id": "123", "content": "Reference content"}]
        updated_conversation = ConversationService.update_reference(
            session=db_session,
            conversation_id=conversation.id,
            reference=new_reference
        )
        
        assert updated_conversation is not None
        assert updated_conversation.reference == new_reference
        
        # Verify the update was persisted
        reloaded_conversation = db_session.query(Conversation).filter(
            Conversation.id == conversation.id
        ).first()
        assert reloaded_conversation.reference == new_reference 