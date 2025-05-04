import pytest
from datetime import datetime
import time

from api.db.sql_service.services.dialog_service import DialogService
from api.utils import get_uuid


class TestDialogService:
    @pytest.fixture
    def test_dialog_data(self, test_tenant):
        """Fixture providing test dialog data."""
        return {
            "tenant_id": test_tenant.id,
            "name": "Test Dialog",
            "description": "Test dialog description",
            "prompt_type": "simple",
            "prompt_config": {
                "system": "Test system prompt",
                "prologue": "Test prologue",
                "parameters": [],
                "empty_response": "Test empty response"
            },
            "llm_id": "test_llm_id",
            "rerank_id": "test_rerank_id",
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
            "kb_ids": []
        }

    def test_create_dialog(self, test_dialog_data, db_session):
        """Test creating a new dialog."""
        dialog = DialogService.save(session=db_session, **test_dialog_data)
        
        assert dialog is not None
        assert dialog.id is not None
        assert dialog.tenant_id == test_dialog_data["tenant_id"]
        assert dialog.name == test_dialog_data["name"]
        assert dialog.description == test_dialog_data["description"]
        assert dialog.prompt_type == test_dialog_data["prompt_type"]
        assert dialog.prompt_config == test_dialog_data["prompt_config"]
        assert dialog.llm_setting == test_dialog_data["llm_setting"]
        assert dialog.similarity_threshold == test_dialog_data["similarity_threshold"]
        assert dialog.vector_similarity_weight == test_dialog_data["vector_similarity_weight"]
        assert dialog.top_n == test_dialog_data["top_n"]
        assert dialog.top_k == test_dialog_data["top_k"]
        assert dialog.do_refer == test_dialog_data["do_refer"]
        assert dialog.kb_ids == test_dialog_data["kb_ids"]
        assert dialog.create_time is not None
        assert dialog.create_date is not None
        assert dialog.update_time is not None
        assert dialog.update_date is not None

    def test_get_by_tenant(self, test_dialog_data, db_session):
        """Test getting dialogs by tenant ID."""
        # Create a dialog
        dialog = DialogService.save(session=db_session, **test_dialog_data)
        
        # Get dialogs for the tenant
        dialogs = DialogService.get_by_tenant(
            session=db_session,
            tenant_id=test_dialog_data["tenant_id"]
        )
        
        assert len(dialogs) == 1
        assert dialogs[0].id == dialog.id
        assert dialogs[0].tenant_id == test_dialog_data["tenant_id"]

    def test_get_with_conversations(self, test_dialog_data, db_session):
        """Test getting a dialog with its conversations."""
        # Create a dialog
        dialog = DialogService.save(session=db_session, **test_dialog_data)
        
        # Get dialog with conversations
        dialog_with_convs = DialogService.get_with_conversations(
            session=db_session,
            dialog_id=dialog.id
        )
        
        assert dialog_with_convs is not None
        assert dialog_with_convs.id == dialog.id
        assert hasattr(dialog_with_convs, "conversations")
        assert isinstance(dialog_with_convs.conversations, list)

    def test_update_settings(self, test_dialog_data, db_session):
        """Test updating dialog settings."""
        # Create a dialog
        dialog = DialogService.save(session=db_session, **test_dialog_data)
        
        # Update settings
        new_settings = {
            "name": "Updated Dialog Name",
            "description": "Updated description",
            "similarity_threshold": 0.3,
            "top_n": 8
        }
        
        updated_dialog = DialogService.update_settings(
            session=db_session,
            dialog_id=dialog.id,
            settings=new_settings
        )
        
        assert updated_dialog is not None
        assert updated_dialog.name == new_settings["name"]
        assert updated_dialog.description == new_settings["description"]
        assert updated_dialog.similarity_threshold == new_settings["similarity_threshold"]
        assert updated_dialog.top_n == new_settings["top_n"]
        
        # Verify that the update happened by checking the updated fields
        dialog_from_db = db_session.query(DialogService.model_class).filter(
            DialogService.model_class.id == dialog.id
        ).first()
        
        assert dialog_from_db.name == new_settings["name"]
        assert dialog_from_db.description == new_settings["description"]
        assert dialog_from_db.similarity_threshold == new_settings["similarity_threshold"]
        assert dialog_from_db.top_n == new_settings["top_n"] 