from datetime import datetime
from typing import List, Dict, Any, Optional
import time

from sqlalchemy.orm import Session
from sqlalchemy import and_, update, func, select, text

from api.db.sql_service.services.base import BaseService, session_context
from api.db.sql_service.models.models import Document
from api.db import StatusEnum, ParserType
from api.utils import get_uuid, current_timestamp, datetime_format


class DocumentService(BaseService):
    """Service class for managing documents."""
    model_class = Document
    
    @classmethod
    @session_context
    def save(cls, session: Session, **kwargs):
        """Save a new document.
        
        Args:
            session: SQLAlchemy session
            **kwargs: Document field values
            
        Returns:
            Created document instance
        """
        if "id" not in kwargs:
            kwargs["id"] = get_uuid()
            
        # Set default values if not provided
        if "parser_id" not in kwargs:
            kwargs["parser_id"] = ParserType.NAIVE.value
        if "parser_config" not in kwargs:
            kwargs["parser_config"] = {"pages": [[1, 1000000]]}
        if "source_type" not in kwargs:
            kwargs["source_type"] = "local"
        if "progress" not in kwargs:
            kwargs["progress"] = 0.0
        if "progress_msg" not in kwargs:
            kwargs["progress_msg"] = ""
        if "run" not in kwargs:
            kwargs["run"] = "0"
            
        # Set timestamps
        now = datetime.now()
        current_time = current_timestamp()
        kwargs['create_time'] = current_time
        kwargs['create_date'] = now
        kwargs['update_time'] = current_time
        kwargs['update_date'] = now
        
        # Create instance
        document = cls.model_class(**kwargs)
        session.add(document)
        session.flush()
        
        return document
    
    @classmethod
    @session_context
    def get_by_knowledgebase(cls, session: Session, kb_id: str):
        """Get all documents for a knowledge base.
        
        Args:
            session: SQLAlchemy session
            kb_id: Knowledge base ID
            
        Returns:
            List of document instances
        """
        return session.query(cls.model_class).filter(
            cls.model_class.kb_id == kb_id,
            cls.model_class.status == StatusEnum.VALID.value
        ).all()
    
    @classmethod
    @session_context
    def update_progress(cls, session: Session, doc_id: str, progress: float,
                       progress_msg: str = None, process_begin_at: datetime = None):
        """Update document processing progress.
        
        Args:
            session: SQLAlchemy session
            doc_id: Document ID
            progress: New progress value (0-1)
            progress_msg: Progress message
            process_begin_at: When processing began
            
        Returns:
            Updated document instance or None if not found
        """
        # Get current document
        document = session.query(cls.model_class).filter(
            cls.model_class.id == doc_id
        ).first()
        
        if not document:
            return None
            
        # Add a small delay to ensure timestamps are different
        time.sleep(0.001)  # 1 millisecond delay
            
        # Update document
        document.progress = progress
        document.update_time = current_timestamp()
        document.update_date = datetime.now()
        
        if progress_msg is not None:
            document.progress_msg = progress_msg
        if process_begin_at is not None:
            document.process_begin_at = process_begin_at
            if progress == 1.0:
                document.process_duation = (datetime.now() - process_begin_at).total_seconds()
        
        session.flush()
        session.commit()
        session.refresh(document)  # Refresh to get fresh data
        return document
    
    @classmethod
    @session_context
    def update_processing_status(cls, session: Session, doc_id: str, run: str):
        """Update document processing status.
        
        Args:
            session: SQLAlchemy session
            doc_id: Document ID
            run: Processing status ("0" for not running, "1" for running)
            
        Returns:
            Updated document instance or None if not found
        """
        # Get current document
        document = session.query(cls.model_class).filter(
            cls.model_class.id == doc_id
        ).first()
        
        if not document:
            return None
            
        # Add a small delay to ensure timestamps are different
        time.sleep(0.001)  # 1 millisecond delay
            
        # Update document
        document.run = run
        document.update_time = current_timestamp()
        document.update_date = datetime.now()
        
        session.flush()
        session.commit()
        session.refresh(document)  # Refresh to get fresh data
        return document 