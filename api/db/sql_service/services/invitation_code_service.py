from datetime import datetime
from typing import List, Dict, Any, Optional
import time

from sqlalchemy.orm import Session

from api.db.sql_service.services.base import BaseService, session_context
from api.db.sql_service.models.models import InvitationCode
from api.db import StatusEnum
from api.utils import get_uuid, current_timestamp, datetime_format


class InvitationCodeService(BaseService):
    """Service class for managing invitation codes."""
    model_class = InvitationCode
    
    @classmethod
    @session_context
    def save(cls, session: Session, **kwargs):
        """Save a new invitation code.
        
        Args:
            session: SQLAlchemy session
            **kwargs: Invitation code field values
            
        Returns:
            Created invitation code instance
        """
        if "id" not in kwargs:
            kwargs["id"] = get_uuid()
            
        # Set timestamps
        now = datetime.now()
        current_time = current_timestamp()
        kwargs['create_time'] = current_time
        kwargs['create_date'] = now
        kwargs['update_time'] = current_time
        kwargs['update_date'] = now
        
        # Create instance
        invitation_code = cls.model_class(**kwargs)
        session.add(invitation_code)
        session.flush()
        
        return invitation_code
    
    @classmethod
    @session_context
    def get_by_code(cls, session: Session, code: str):
        """Get an invitation code by its code value.
        
        Args:
            session: SQLAlchemy session
            code: The invitation code to look up
            
        Returns:
            Invitation code instance or None if not found
        """
        return session.query(cls.model_class).filter(
            cls.model_class.code == code,
            cls.model_class.status == StatusEnum.VALID.value
        ).first()
    
    @classmethod
    @session_context
    def mark_as_used(cls, session: Session, code_id: str, user_id: str):
        """Mark an invitation code as used.
        
        Args:
            session: SQLAlchemy session
            code_id: ID of the invitation code
            user_id: ID of the user who used the code
            
        Returns:
            Updated invitation code instance or None if not found
        """
        code = session.query(cls.model_class).filter(
            cls.model_class.id == code_id
        ).first()
        
        if not code:
            return None
            
        # Add a small delay to ensure timestamps are different
        time.sleep(0.001)  # 1 millisecond delay
            
        # Update timestamps
        current_time = current_timestamp()
        current_date = datetime.now()
        code.update_time = current_time
        code.update_date = current_date
        
        # Mark as used
        code.visit_time = current_date
        code.user_id = user_id
        code.status = StatusEnum.INVALID.value
        
        session.flush()
        return code 