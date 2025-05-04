from datetime import datetime
from beartype.typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from api.db.sql_service.services.base import BaseService, session_context
from api.db.sql_service.models.models import File2Document
from api.utils import get_uuid, current_timestamp, datetime_format


class File2DocumentService(BaseService):
    """Service class for managing file-document associations."""
    model_class = File2Document
    
    @classmethod
    @session_context
    def save(cls, session: Session, **kwargs):
        """Save a new file-document association.
        
        Args:
            session: SQLAlchemy session
            **kwargs: Association field values
            
        Returns:
            Created association instance
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
        association = cls.model_class(**kwargs)
        session.add(association)
        session.flush()
        
        return association
    
    @classmethod
    @session_context
    def get_by_file(cls, session: Session, file_id: str):
        """Get document associations for a file.
        
        Args:
            session: SQLAlchemy session
            file_id: File ID
            
        Returns:
            List of association instances
        """
        return session.query(cls.model_class).filter(
            cls.model_class.file_id == file_id
        ).all()
    
    @classmethod
    @session_context
    def get_by_document(cls, session: Session, document_id: str):
        """Get file associations for a document.
        
        Args:
            session: SQLAlchemy session
            document_id: Document ID
            
        Returns:
            List of association instances
        """
        return session.query(cls.model_class).filter(
            cls.model_class.document_id == document_id
        ).all()
    
    @classmethod
    @session_context
    def delete_by_file(cls, session: Session, file_id: str):
        """Delete all associations for a file.
        
        Args:
            session: SQLAlchemy session
            file_id: File ID
            
        Returns:
            Number of associations deleted
        """
        associations = session.query(cls.model_class).filter(
            cls.model_class.file_id == file_id
        ).all()
        
        count = len(associations)
        for association in associations:
            session.delete(association)
            
        session.flush()
        return count
    
    @classmethod
    @session_context
    def delete_by_document(cls, session: Session, document_id: str):
        """Delete all associations for a document.
        
        Args:
            session: SQLAlchemy session
            document_id: Document ID
            
        Returns:
            Number of associations deleted
        """
        associations = session.query(cls.model_class).filter(
            cls.model_class.document_id == document_id
        ).all()
        
        count = len(associations)
        for association in associations:
            session.delete(association)
            
        session.flush()
        return count 