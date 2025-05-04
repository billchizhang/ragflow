from datetime import datetime
from beartype.typing import List, Dict, Any, Type, Optional, Tuple, Union
from functools import wraps

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from api.db.sql_service.database import get_db_session
from api.db.sql_service.models.base import BaseModel
from api.utils import get_uuid, current_timestamp, datetime_format


def session_context(func):
    """Decorator to provide a session for database operations.
    
    This decorator manages creating and closing a database session for the decorated method.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function with session context handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if session is already provided
        session = kwargs.get('session')
        session_provided = session is not None
        
        try:
            if not session_provided:
                # Create new session
                with get_db_session() as session:
                    kwargs['session'] = session
                    result = func(*args, **kwargs)
                    session.commit()
                    return result
            else:
                # Use provided session
                result = func(*args, **kwargs)
                session.commit()  # Commit changes even when session is provided
                return result
        except Exception as e:
            if session:
                session.rollback()
            raise e
    return wrapper


class BaseService:
    """Base service class that provides common database operations.
    
    This service encapsulates common database operations for all model types,
    implementing patterns that are used across all services.
    
    Attributes:
        model_class: The SQLAlchemy model class this service operates on
    """
    model_class = None
    
    @classmethod
    @session_context
    def query(cls, session: Session, cols=None, reverse=None, order_by=None, **filters):
        """Execute a database query with filters and ordering.
        
        This method provides a flexible way to query the database with various filters
        and sorting options.
        
        Args:
            session: SQLAlchemy session
            cols: List of column names to select
            reverse: Boolean indicating sort direction (True for desc, False for asc)
            order_by: Column name to sort by
            **filters: Filter criteria as keyword arguments
            
        Returns:
            List of model instances matching the criteria
        """
        query = session.query(cls.model_class)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(cls.model_class, key):
                # Handle list/set values as IN condition
                attr = getattr(cls.model_class, key)
                if isinstance(value, (list, set)):
                    query = query.filter(attr.in_(value))
                else:
                    query = query.filter(attr == value)
        
        # Apply ordering
        if reverse is not None:
            if order_by is None:
                order_by = 'create_time'
            
            if hasattr(cls.model_class, order_by):
                order_attr = getattr(cls.model_class, order_by)
                if reverse:
                    query = query.order_by(desc(order_attr))
                else:
                    query = query.order_by(asc(order_attr))
        
        return query.all()
    
    @classmethod
    @session_context
    def get_all(cls, session: Session, cols=None, reverse=None, order_by=None):
        """Retrieve all records with optional ordering.
        
        Args:
            session: SQLAlchemy session
            cols: List of column names to select
            reverse: Boolean indicating sort direction (True for desc, False for asc)
            order_by: Column name to sort by
            
        Returns:
            List of all model instances with optional ordering
        """
        query = session.query(cls.model_class)
        
        # Apply ordering
        if reverse is not None:
            if order_by is None:
                order_by = 'create_time'
            
            if hasattr(cls.model_class, order_by):
                order_attr = getattr(cls.model_class, order_by)
                if reverse:
                    query = query.order_by(desc(order_attr))
                else:
                    query = query.order_by(asc(order_attr))
        
        return query.all()
    
    @classmethod
    @session_context
    def get(cls, session: Session, **filters):
        """Get a single record that matches the filters.
        
        Args:
            session: SQLAlchemy session
            **filters: Filter criteria as keyword arguments
            
        Returns:
            Model instance or None if not found
        """
        query = session.query(cls.model_class)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(cls.model_class, key):
                query = query.filter(getattr(cls.model_class, key) == value)
        
        return query.first()
    
    @classmethod
    @session_context
    def get_or_none(cls, session: Session, **filters):
        """Get a single record or None if not found.
        
        This is identical to get() but makes the intent clearer.
        
        Args:
            session: SQLAlchemy session
            **filters: Filter criteria as keyword arguments
            
        Returns:
            Model instance or None if not found
        """
        return cls.get(session=session, **filters)
    
    @classmethod
    @session_context
    def save(cls, session: Session, **data):
        """Save a new record to the database.
        
        Args:
            session: SQLAlchemy session
            **data: Record field values as keyword arguments
            
        Returns:
            Created model instance
        """
        # Generate ID if not provided
        if "id" not in data:
            data["id"] = get_uuid()
            
        # Set timestamps
        current_time = current_timestamp()
        current_date = datetime.now()
        data["create_time"] = current_time
        data["create_date"] = current_date
        data["update_time"] = current_time
        data["update_date"] = current_date
        
        # Create an instance
        instance = cls.model_class(**data)
        
        # Add and commit
        session.add(instance)
        session.flush()  # Flush to get the ID
        
        return instance
    
    @classmethod
    @session_context
    def insert(cls, session: Session, **data):
        """Insert a new record with auto-generated ID and timestamps.
        
        Args:
            session: SQLAlchemy session
            **data: Record field values as keyword arguments
            
        Returns:
            Created model instance
        """
        # Add ID if not provided
        if 'id' not in data:
            data['id'] = get_uuid()
        
        # Add timestamps
        now = datetime.now()
        current_time = current_timestamp()
        data['create_time'] = current_time
        data['create_date'] = now
        data['update_time'] = current_time
        data['update_date'] = now
        
        # Create instance
        instance = cls.model_class(**data)
        
        # Add and commit
        session.add(instance)
        session.flush()
        
        return instance
    
    @classmethod
    @session_context
    def insert_many(cls, session: Session, data_list: List[Dict], batch_size=100):
        """Insert multiple records in batches.
        
        Args:
            session: SQLAlchemy session
            data_list: List of dictionaries containing record data
            batch_size: Number of records to insert in each batch
        """
        # Add timestamps to all records
        now = datetime.now()
        current_time = current_timestamp()
        
        for data in data_list:
            data['create_time'] = current_time
            data['create_date'] = now
            
            # Create instance
            instance = cls.model_class(**data)
            session.add(instance)
            
        # Commit in batches
        session.flush()
    
    @classmethod
    @session_context
    def update_many_by_id(cls, session: Session, data_list: List[Dict]):
        """Update multiple records by their IDs.
        
        Args:
            session: SQLAlchemy session
            data_list: List of dictionaries containing record data with 'id' field
        """
        # Set update timestamps
        now = datetime.now()
        current_time = current_timestamp()
        
        for data in data_list:
            if 'id' not in data:
                continue
                
            record_id = data.pop('id')
            data['update_time'] = current_time
            data['update_date'] = now
            
            # Get instance
            instance = session.query(cls.model_class).filter(
                cls.model_class.id == record_id).first()
                
            if instance:
                # Update fields
                for key, value in data.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
        
        # Commit changes
        session.flush()
    
    @classmethod
    @session_context
    def update_by_id(cls, session: Session, record_id: str, data: Dict):
        """Update a record by its ID.
        
        Args:
            session: SQLAlchemy session
            record_id: Record's ID
            data: Dictionary of field values to update
            
        Returns:
            Updated model instance or None if not found
        """
        instance = session.query(cls.model_class).filter(
            cls.model_class.id == record_id
        ).first()
        
        if not instance:
            return None
            
        # Update timestamps first
        current_time = current_timestamp()
        current_date = datetime.now()
        instance.update_time = current_time
        instance.update_date = current_date
            
        # Update fields
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        session.flush()
        session.refresh(instance)
        return instance
    
    @classmethod
    @session_context
    def get_by_id(cls, session: Session, record_id: str):
        """Get a record by its ID.
        
        Args:
            session: SQLAlchemy session
            record_id: Record's ID
            
        Returns:
            Model instance or None if not found
        """
        return session.query(cls.model_class).filter(
            cls.model_class.id == record_id
        ).first()
    
    @classmethod
    @session_context
    def get_by_ids(cls, session: Session, record_ids: List[str], cols=None):
        """Get multiple records by their IDs.
        
        Args:
            session: SQLAlchemy session
            record_ids: List of record IDs to retrieve
            cols: Optional list of column names to select
            
        Returns:
            List of matching records
        """
        query = session.query(cls.model_class).filter(
            cls.model_class.id.in_(record_ids))
            
        return query.all()
    
    @classmethod
    @session_context
    def delete_by_id(cls, session: Session, record_id: str):
        """Delete a record by ID.
        
        Args:
            session: SQLAlchemy session
            record_id: ID of the record to delete
            
        Returns:
            Number of records deleted (0 or 1)
        """
        instance = session.query(cls.model_class).filter(
            cls.model_class.id == record_id).first()
            
        if instance:
            session.delete(instance)
            return 1
        return 0
    
    @classmethod
    @session_context
    def filter_delete(cls, session: Session, filters: List):
        """Delete records matching given filter conditions.
        
        Args:
            session: SQLAlchemy session
            filters: List of SQLAlchemy filter conditions
            
        Returns:
            Number of records deleted
        """
        query = session.query(cls.model_class)
        
        for filter_condition in filters:
            query = query.filter(filter_condition)
            
        instances = query.all()
        count = len(instances)
        
        for instance in instances:
            session.delete(instance)
            
        return count
    
    @classmethod
    @session_context
    def filter_update(cls, session: Session, filters: List, update_data: Dict):
        """Update records matching given filter conditions.
        
        Args:
            session: SQLAlchemy session
            filters: List of SQLAlchemy filter conditions
            update_data: Dictionary of fields to update
            
        Returns:
            Number of records updated
        """
        # Set update timestamps
        now = datetime.now()
        update_data['update_time'] = current_timestamp()
        update_data['update_date'] = now
        
        query = session.query(cls.model_class)
        
        for filter_condition in filters:
            query = query.filter(filter_condition)
            
        instances = query.all()
        count = len(instances)
        
        for instance in instances:
            for key, value in update_data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                    
        return count
    
    @staticmethod
    def cut_list(target_list, n):
        """Split a list into chunks of size n.
        
        Args:
            target_list: List to split
            n: Chunk size
            
        Returns:
            List of chunks
        """
        return [target_list[i:i + n] for i in range(0, len(target_list), n)]
        
    @classmethod
    @session_context
    def filter_scope_list(cls, session: Session, in_key: str, in_filters_list: List,
                        filters=None, cols=None):
        """Get records matching IN clause filters.
        
        Args:
            session: SQLAlchemy session
            in_key: Field name for IN clause
            in_filters_list: List of values for IN clause
            filters: Additional filter conditions
            cols: List of columns to select
            
        Returns:
            List of matching records
        """
        if not in_filters_list:
            return []
            
        if not hasattr(cls.model_class, in_key):
            return []
            
        # Break up large IN clauses into smaller chunks to avoid database limits
        all_results = []
        chunked_lists = cls.cut_list(in_filters_list, 500)
        
        for chunk in chunked_lists:
            query = session.query(cls.model_class)
            query = query.filter(getattr(cls.model_class, in_key).in_(chunk))
            
            if filters:
                for filter_condition in filters:
                    query = query.filter(filter_condition)
                    
            results = query.all()
            all_results.extend(results)
            
        return all_results 