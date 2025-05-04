from datetime import datetime
from typing import List, Dict, Any, Optional
import time

from sqlalchemy.orm import Session
from sqlalchemy import and_

from api.db.sql_service.services.base import BaseService, session_context
from api.db.sql_service.models.models import File
from api.db import StatusEnum
from api.utils import get_uuid, current_timestamp, datetime_format


class FileService(BaseService):
    """Service class for managing files."""
    model_class = File
    
    @classmethod
    @session_context
    def save(cls, session: Session, **kwargs):
        """Save a new file.
        
        Args:
            session: SQLAlchemy session
            **kwargs: File field values
            
        Returns:
            Created file instance
        """
        if "id" not in kwargs:
            kwargs["id"] = get_uuid()
            
        # Set default values if not provided
        if "source_type" not in kwargs:
            kwargs["source_type"] = ""
            
        # Set timestamps
        now = datetime.now()
        current_time = current_timestamp()
        kwargs['create_time'] = current_time
        kwargs['create_date'] = now
        kwargs['update_time'] = current_time
        kwargs['update_date'] = now
        
        # Create instance
        file = cls.model_class(**kwargs)
        session.add(file)
        session.flush()
        
        return file
    
    @classmethod
    @session_context
    def get_by_tenant(cls, session: Session, tenant_id: str):
        """Get all files for a tenant.
        
        Args:
            session: SQLAlchemy session
            tenant_id: Tenant ID
            
        Returns:
            List of file instances
        """
        return session.query(cls.model_class).filter(
            cls.model_class.tenant_id == tenant_id
        ).all()
    
    @classmethod
    @session_context
    def get_by_parent(cls, session: Session, parent_id: str):
        """Get all files in a parent directory.
        
        Args:
            session: SQLAlchemy session
            parent_id: Parent directory ID
            
        Returns:
            List of file instances
        """
        return session.query(cls.model_class).filter(
            cls.model_class.parent_id == parent_id
        ).all()
    
    @classmethod
    @session_context
    def update_location(cls, session: Session, file_id: str, location: str):
        """Update file location.
        
        Args:
            session: SQLAlchemy session
            file_id: File ID
            location: New file location
            
        Returns:
            Updated file instance or None if not found
        """
        file = session.query(cls.model_class).filter(
            cls.model_class.id == file_id
        ).first()
        
        if not file:
            return None
            
        # Add a small delay to ensure timestamps are different
        time.sleep(0.001)  # 1 millisecond delay
            
        # Update timestamps
        current_time = current_timestamp()
        current_date = datetime.now()
        file.update_time = current_time
        file.update_date = current_date
        
        # Update location
        file.location = location
        
        session.flush()
        return file 