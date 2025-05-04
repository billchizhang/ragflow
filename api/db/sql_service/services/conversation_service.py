from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from api.db.sql_service.models.models import Conversation
from api.db.sql_service.services.base import BaseService
from api.utils import get_uuid, current_timestamp, datetime_format


class ConversationService(BaseService):
    """Service for managing conversations."""

    @classmethod
    def save(cls, session: Session, **kwargs) -> Conversation:
        """Save a new conversation.
        
        Args:
            session: SQLAlchemy session
            **kwargs: Conversation data
            
        Returns:
            Conversation: The saved conversation
        """
        if "id" not in kwargs:
            kwargs["id"] = get_uuid()
        
        # Set timestamps
        current_time = current_timestamp()
        kwargs["create_time"] = current_time
        kwargs["create_date"] = datetime.fromtimestamp(current_time / 1_000_000)
        kwargs["update_time"] = current_time
        kwargs["update_date"] = datetime.fromtimestamp(current_time / 1_000_000)
        
        # Set default values
        if "message" not in kwargs:
            kwargs["message"] = []
        if "reference" not in kwargs:
            kwargs["reference"] = []
        if "status" not in kwargs:
            kwargs["status"] = "1"
            
        conversation = Conversation(**kwargs)
        session.add(conversation)
        session.flush()
        return conversation

    @classmethod
    def get_by_dialog(cls, session: Session, dialog_id: str, status: str = "1") -> List[Conversation]:
        """Get all conversations for a dialog.
        
        Args:
            session: SQLAlchemy session
            dialog_id: Dialog ID
            status: Status filter
            
        Returns:
            List[Conversation]: List of conversations
        """
        return session.query(Conversation).filter(
            Conversation.dialog_id == dialog_id,
            Conversation.status == status
        ).order_by(Conversation.create_time.desc()).all()

    @classmethod
    def update_message(cls, session: Session, conversation_id: str, message: List[Dict]) -> Optional[Conversation]:
        """Update a conversation's message.
        
        Args:
            session: SQLAlchemy session
            conversation_id: Conversation ID
            message: New message
            
        Returns:
            Optional[Conversation]: Updated conversation or None if not found
        """
        conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return None
            
        current_time = current_timestamp()
        conversation.message = message
        conversation.update_time = current_time
        conversation.update_date = datetime.fromtimestamp(current_time / 1_000_000)
        
        session.flush()
        session.commit()
        return conversation

    @classmethod
    def update_reference(cls, session: Session, conversation_id: str, reference: List[Dict]) -> Optional[Conversation]:
        """Update a conversation's reference.
        
        Args:
            session: SQLAlchemy session
            conversation_id: Conversation ID
            reference: New reference
            
        Returns:
            Optional[Conversation]: Updated conversation or None if not found
        """
        conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return None
            
        current_time = current_timestamp()
        conversation.reference = reference
        conversation.update_time = current_time
        conversation.update_date = datetime.fromtimestamp(current_time / 1_000_000)
        
        session.flush()
        session.commit()
        return conversation 