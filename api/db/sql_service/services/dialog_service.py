from datetime import datetime
from beartype.typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from api.db.sql_service.services.base import BaseService, session_context
from api.db.sql_service.models.models import Dialog, Conversation
from api.db import StatusEnum
from api.utils import get_uuid, current_timestamp, datetime_format


class DialogService(BaseService):
    """Service class for managing dialogs."""
    model_class = Dialog
    
    @classmethod
    @session_context
    def save(cls, session: Session, **kwargs):
        """Save a new dialog.
        
        Args:
            session: SQLAlchemy session
            **kwargs: Dialog field values
            
        Returns:
            Created dialog instance
        """
        if "id" not in kwargs:
            kwargs["id"] = get_uuid()
            
        # Set default values if not provided
        if "prompt_type" not in kwargs:
            kwargs["prompt_type"] = "simple"
        if "prompt_config" not in kwargs:
            kwargs["prompt_config"] = {
                "system": "",
                "prologue": "Hi! I'm your assistant, what can I do for you?",
                "parameters": [],
                "empty_response": "Sorry! No relevant content was found in the knowledge base!"
            }
        if "llm_setting" not in kwargs:
            kwargs["llm_setting"] = {
                "temperature": 0.1,
                "top_p": 0.3,
                "frequency_penalty": 0.7,
                "presence_penalty": 0.4,
                "max_tokens": 512
            }
        if "similarity_threshold" not in kwargs:
            kwargs["similarity_threshold"] = 0.2
        if "vector_similarity_weight" not in kwargs:
            kwargs["vector_similarity_weight"] = 0.3
        if "top_n" not in kwargs:
            kwargs["top_n"] = 6
        if "top_k" not in kwargs:
            kwargs["top_k"] = 1024
        if "do_refer" not in kwargs:
            kwargs["do_refer"] = "1"
        if "kb_ids" not in kwargs:
            kwargs["kb_ids"] = []
            
        # Set timestamps
        now = datetime.now()
        current_time = current_timestamp()
        kwargs['create_time'] = current_time
        kwargs['create_date'] = now
        kwargs['update_time'] = current_time
        kwargs['update_date'] = now
        
        # Create instance
        dialog = cls.model_class(**kwargs)
        session.add(dialog)
        session.flush()
        
        return dialog
    
    @classmethod
    @session_context
    def get_by_tenant(cls, session: Session, tenant_id: str):
        """Get all dialogs for a tenant.
        
        Args:
            session: SQLAlchemy session
            tenant_id: Tenant ID
            
        Returns:
            List of dialog instances
        """
        return session.query(cls.model_class).filter(
            cls.model_class.tenant_id == tenant_id,
            cls.model_class.status == StatusEnum.VALID.value
        ).all()
    
    @classmethod
    @session_context
    def get_with_conversations(cls, session: Session, dialog_id: str):
        """Get a dialog with its conversations.
        
        Args:
            session: SQLAlchemy session
            dialog_id: Dialog ID
            
        Returns:
            Dialog instance with conversations
        """
        dialog = session.query(cls.model_class).filter(
            cls.model_class.id == dialog_id,
            cls.model_class.status == StatusEnum.VALID.value
        ).first()
        
        if dialog:
            dialog.conversations = session.query(Conversation).filter(
                Conversation.dialog_id == dialog_id
            ).all()
            
        return dialog
    
    @classmethod
    @session_context
    def update_settings(cls, session: Session, dialog_id: str, settings: Dict):
        """Update dialog settings.
        
        Args:
            session: SQLAlchemy session
            dialog_id: Dialog ID
            settings: Dictionary of settings to update
            
        Returns:
            Updated dialog instance or None if not found
        """
        dialog = session.query(cls.model_class).filter(
            cls.model_class.id == dialog_id
        ).first()
        
        if not dialog:
            return None
            
        # Update timestamps
        current_time = current_timestamp()
        current_date = datetime.now()
        dialog.update_time = current_time
        dialog.update_date = current_date
        
        # Update settings
        for key, value in settings.items():
            if hasattr(dialog, key):
                setattr(dialog, key, value)
                
        session.flush()
        return dialog 