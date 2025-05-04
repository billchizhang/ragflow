from beartype.typing import List, Dict

from sqlalchemy import and_
from sqlalchemy.orm import Session

from api.db.sql_service.services.base import BaseService, session_context
from api.db.sql_service.models.models import User, UserTenant, Tenant
from api.db import StatusEnum
from api.utils import get_uuid


class UserTenantService(BaseService):
    """Service class for managing user-tenant relationships.
    
    This service handles the many-to-many relationship between users and tenants,
    including user roles and tenant membership.
    
    Attributes:
        model_class: The UserTenant model class for database operations
    """
    model_class = UserTenant
    
    @classmethod
    @session_context
    def save(cls, session: Session, **kwargs):
        """Save a new user-tenant relationship.
        
        Args:
            session: SQLAlchemy session
            **kwargs: Relationship field values
            
        Returns:
            Created relationship instance
        """
        if "id" not in kwargs:
            kwargs["id"] = get_uuid()
            
        # Create instance
        user_tenant = cls.model_class(**kwargs)
        session.add(user_tenant)
        session.flush()
        
        return user_tenant
    
    @classmethod
    @session_context
    def get_users_by_tenant_id(cls, session: Session, tenant_id: str):
        """Get all users associated with a tenant.
        
        Args:
            session: SQLAlchemy session
            tenant_id: Tenant's ID
            
        Returns:
            List of User instances
        """
        return session.query(User).join(
            cls.model_class,
            and_(
                cls.model_class.user_id == User.id,
                cls.model_class.tenant_id == tenant_id,
                cls.model_class.status == StatusEnum.VALID.value
            )
        ).filter(
            User.status == StatusEnum.VALID.value
        ).all()
    
    @classmethod
    @session_context
    def get_tenants_by_user_id(cls, session: Session, user_id: str):
        """Get all tenants associated with a user.
        
        Args:
            session: SQLAlchemy session
            user_id: User's ID
            
        Returns:
            List of Tenant instances
        """
        return session.query(Tenant).join(
            cls.model_class,
            and_(
                cls.model_class.tenant_id == Tenant.id,
                cls.model_class.user_id == user_id,
                cls.model_class.status == StatusEnum.VALID.value
            )
        ).filter(
            Tenant.status == StatusEnum.VALID.value
        ).all() 