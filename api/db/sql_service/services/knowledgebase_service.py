from datetime import datetime
from beartype.typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from api.db.sql_service.services.base import BaseService, session_context
from api.db.sql_service.models.models import Knowledgebase, Document
from api.db import StatusEnum, ParserType, TenantPermission
from api.utils import get_uuid, current_timestamp, datetime_format


class KnowledgebaseService(BaseService):
    """Service class for managing knowledge bases."""
    model_class = Knowledgebase
    
    @classmethod
    @session_context
    def save(cls, session: Session, **kwargs):
        """Save a new knowledge base.
        
        Args:
            session: SQLAlchemy session
            **kwargs: Knowledge base field values
            
        Returns:
            Created knowledge base instance
        """
        if "id" not in kwargs:
            kwargs["id"] = get_uuid()
            
        # Set default values if not provided
        if "parser_id" not in kwargs:
            kwargs["parser_id"] = ParserType.NAIVE.value
        if "parser_config" not in kwargs:
            kwargs["parser_config"] = {"pages": [[1, 1000000]]}
        if "permission" not in kwargs:
            kwargs["permission"] = TenantPermission.ME.value
        if "similarity_threshold" not in kwargs:
            kwargs["similarity_threshold"] = 0.2
        if "vector_similarity_weight" not in kwargs:
            kwargs["vector_similarity_weight"] = 0.3
            
        # Set timestamps
        now = datetime.now()
        current_time = current_timestamp()
        kwargs['create_time'] = current_time
        kwargs['create_date'] = now
        kwargs['update_time'] = current_time
        kwargs['update_date'] = now
        
        # Create instance
        knowledgebase = cls.model_class(**kwargs)
        session.add(knowledgebase)
        session.flush()
        
        return knowledgebase
    
    @classmethod
    @session_context
    def get_by_tenant(cls, session: Session, tenant_id: str):
        """Get all knowledge bases for a tenant.
        
        Args:
            session: SQLAlchemy session
            tenant_id: Tenant's ID
            
        Returns:
            List of knowledge base instances
        """
        return session.query(cls.model_class).filter(
            cls.model_class.tenant_id == tenant_id,
            cls.model_class.status == StatusEnum.VALID.value
        ).all()
    
    @classmethod
    @session_context
    def get_with_documents(cls, session: Session, kb_id: str):
        """Get a knowledge base with its documents.
        
        Args:
            session: SQLAlchemy session
            kb_id: Knowledge base ID
            
        Returns:
            Knowledge base instance with documents
        """
        kb = session.query(cls.model_class).filter(
            cls.model_class.id == kb_id,
            cls.model_class.status == StatusEnum.VALID.value
        ).first()
        
        if kb:
            kb.documents = session.query(Document).filter(
                Document.kb_id == kb_id,
                Document.status == StatusEnum.VALID.value
            ).all()
            
        return kb
    
    @classmethod
    @session_context
    def update_stats(cls, session: Session, kb_id: str, doc_num: int = None,
                    token_num: int = None, chunk_num: int = None):
        """Update knowledge base statistics.
        
        Args:
            session: SQLAlchemy session
            kb_id: Knowledge base ID
            doc_num: New document count
            token_num: New token count
            chunk_num: New chunk count
            
        Returns:
            Updated knowledge base instance or None if not found
        """
        kb = session.query(cls.model_class).filter(
            cls.model_class.id == kb_id
        ).first()
        
        if not kb:
            return None
            
        # Update timestamps
        current_time = current_timestamp()
        current_date = datetime.now()
        kb.update_time = current_time
        kb.update_date = current_date
        
        # Update stats
        if doc_num is not None:
            kb.doc_num = doc_num
        if token_num is not None:
            kb.token_num = token_num
        if chunk_num is not None:
            kb.chunk_num = chunk_num
            
        session.flush()
        return kb 