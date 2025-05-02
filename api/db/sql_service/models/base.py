from datetime import datetime
import json
from sqlalchemy import BigInteger, DateTime, Column
from sqlalchemy.ext.declarative import declared_attr

from api.db.sql_service.database import Base
from api.utils import get_uuid, current_timestamp, datetime_format


class BaseModel(Base):
    """Base model for all SQLAlchemy models.
    
    This class provides common fields and functionality that are shared
    across all database models. It includes timestamp fields for tracking
    creation and update times.
    
    Attributes:
        create_time (Column): Timestamp when the record was created, stored as BigInteger
        create_date (Column): Datetime when the record was created
        update_time (Column): Timestamp when the record was last updated, stored as BigInteger
        update_date (Column): Datetime when the record was last updated
    """
    __abstract__ = True

    create_time = Column(BigInteger, nullable=True, index=True)
    create_date = Column(DateTime, nullable=True, index=True)
    update_time = Column(BigInteger, nullable=True, index=True)
    update_date = Column(DateTime, nullable=True, index=True)
    
    @declared_attr
    def __tablename__(cls):
        """Automatically generate table name based on class name."""
        return cls.__name__.lower()

    def to_dict(self):
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def to_json(self):
        """Convert model instance to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def create_with_defaults(cls, session, **kwargs):
        """Create a new record with default timestamps."""
        if "id" not in kwargs:
            kwargs["id"] = get_uuid()
        
        # Set timestamps
        current_time = current_timestamp()
        current_date = datetime.now()
        kwargs["create_time"] = current_time
        kwargs["create_date"] = current_date
        kwargs["update_time"] = current_time
        kwargs["update_date"] = current_date
        
        # Create instance and add to session
        instance = cls(**kwargs)
        session.add(instance)
        session.commit()
        return instance
    
    @classmethod
    def update_by_id(cls, session, record_id, data):
        """Update a record by ID.
        
        Args:
            session: SQLAlchemy session
            record_id: ID of the record to update
            data: Dictionary of fields to update
            
        Returns:
            Updated instance if successful, None if record not found
        """
        instance = session.query(cls).filter(cls.id == record_id).first()
        if not instance:
            return None
        
        # Set update timestamps
        data["update_time"] = current_timestamp()
        data["update_date"] = datetime.now()
        
        # Update instance
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        session.commit()
        return instance 