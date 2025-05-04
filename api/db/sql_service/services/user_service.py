import hashlib
from datetime import datetime
from beartype.typing import List, Dict, Any, Optional, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

from api.db.sql_service.services.base import BaseService, session_context
from api.db.sql_service.models.models import User, Tenant, UserTenant
from api.db import UserTenantRole, StatusEnum
from api.utils import get_uuid, current_timestamp, datetime_format
from rag.settings import MINIO


class UserService(BaseService):
    """Service class for managing user-related operations.
    
    This service handles user management, including authentication,
    user creation, and user profiles.
    
    Attributes:
        model_class: The User model class for database operations
    """
    model_class = User
    
    @classmethod
    @session_context
    def filter_by_id(cls, session: Session, user_id: str):
        """Retrieve a user by ID.
        
        Args:
            session: SQLAlchemy session
            user_id: User's unique identifier
            
        Returns:
            User instance or None if not found
        """
        return session.query(cls.model_class).filter(
            cls.model_class.id == user_id).first()
    
    @classmethod
    @session_context
    def query_user(cls, session: Session, email: str, password: str):
        """Authenticate a user with email and password.
        
        Args:
            session: SQLAlchemy session
            email: User's email address
            password: User's password
            
        Returns:
            User instance if authentication successful, None otherwise
        """
        user = session.query(cls.model_class).filter(
            cls.model_class.email == email,
            cls.model_class.status == StatusEnum.VALID.value
        ).first()
        
        if user and check_password_hash(str(user.password), password):
            return user
        return None
    
    @classmethod
    @session_context
    def save(cls, session: Session, **kwargs):
        """Save a new user to the database with password hashing.
        
        Args:
            session: SQLAlchemy session
            **kwargs: User field values
            
        Returns:
            Created user instance
        """
        if "id" not in kwargs:
            kwargs["id"] = get_uuid()
            
        # Hash password if provided
        if "password" in kwargs:
            kwargs["password"] = generate_password_hash(str(kwargs["password"]))
        
        # Set timestamps
        now = datetime.now()
        current_time = current_timestamp()
        kwargs['create_time'] = current_time
        kwargs['create_date'] = now
        kwargs['update_time'] = current_time
        kwargs['update_date'] = now
        
        # Create instance
        user = cls.model_class(**kwargs)
        session.add(user)
        session.flush()
        
        # Refresh the instance to ensure all attributes are loaded
        session.refresh(user)
        return user
    
    @classmethod
    @session_context
    def delete_user(cls, session: Session, user_ids: List[str], update_user_dict: Dict):
        """Delete users by marking them as inactive.
        
        Args:
            session: SQLAlchemy session
            user_ids: List of user IDs to delete
            update_user_dict: Additional fields to update
            
        Returns:
            Number of users deleted
        """
        users = session.query(cls.model_class).filter(
            cls.model_class.id.in_(user_ids)).all()
            
        count = 0
        for user in users:
            # Update timestamps first
            current_time = current_timestamp()
            current_date = datetime.now()
            user.update_time = current_time
            user.update_date = current_date
            
            # Mark as deleted
            user.status = StatusEnum.DELETED.value
            count += 1
            
            # Update additional fields
            for key, value in update_user_dict.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            # Flush changes
            session.flush()
            session.refresh(user)
        
        return count
    
    @classmethod
    @session_context
    def update_user(cls, session: Session, user_id: str, user_dict: Dict):
        """Update a user's information.
        
        Args:
            session: SQLAlchemy session
            user_id: ID of the user to update
            user_dict: Dictionary of fields to update
            
        Returns:
            Updated user instance or None if not found
        """
        user = session.query(cls.model_class).filter(
            cls.model_class.id == user_id).first()
            
        if not user:
            return None
            
        # Update timestamps first
        current_time = current_timestamp()
        current_date = datetime.now()
        user.update_time = current_time
        user.update_date = current_date
        
        # Update fields
        for key, value in user_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        # Flush changes
        session.flush()
        session.refresh(user)
        return user


class TenantService(BaseService):
    """Service class for managing tenant-related operations.
    
    This service handles tenant management, including tenant information
    retrieval and tenant credit management.
    
    Attributes:
        model_class: The Tenant model class for database operations
    """
    model_class = Tenant
    
    @classmethod
    @session_context
    def get_info_by(cls, session: Session, user_id: str):
        """Get tenant information for a user.
        
        Args:
            session: SQLAlchemy session
            user_id: User's ID
            
        Returns:
            List of tenant information dictionaries
        """
        results = session.query(
            cls.model_class.id.label('tenant_id'),
            cls.model_class.name,
            cls.model_class.llm_id,
            cls.model_class.embd_id,
            cls.model_class.rerank_id,
            cls.model_class.asr_id,
            cls.model_class.img2txt_id,
            cls.model_class.tts_id,
            cls.model_class.parser_ids,
            UserTenant.role
        ).join(
            UserTenant, 
            and_(
                cls.model_class.id == UserTenant.tenant_id,
                UserTenant.user_id == user_id,
                UserTenant.status == StatusEnum.VALID.value,
                UserTenant.role == UserTenantRole.OWNER
            )
        ).filter(
            cls.model_class.status == StatusEnum.VALID.value
        ).all()
        
        # Convert results to dictionaries
        return [dict(zip(['tenant_id', 'name', 'llm_id', 'embd_id', 'rerank_id', 
                          'asr_id', 'img2txt_id', 'tts_id', 'parser_ids', 'role'], row)) 
                for row in results]
    
    @classmethod
    @session_context
    def get_joined_tenants_by_user_id(cls, session: Session, user_id: str):
        """Get tenants where the user is a member but not an owner.
        
        Args:
            session: SQLAlchemy session
            user_id: User's ID
            
        Returns:
            List of tenant information dictionaries
        """
        results = session.query(
            cls.model_class.id.label('tenant_id'),
            cls.model_class.name,
            cls.model_class.llm_id,
            cls.model_class.embd_id,
            cls.model_class.asr_id,
            cls.model_class.img2txt_id,
            UserTenant.role
        ).join(
            UserTenant, 
            and_(
                cls.model_class.id == UserTenant.tenant_id,
                UserTenant.user_id == user_id,
                UserTenant.status == StatusEnum.VALID.value,
                UserTenant.role == UserTenantRole.NORMAL
            )
        ).filter(
            cls.model_class.status == StatusEnum.VALID.value
        ).all()
        
        # Convert results to dictionaries
        return [dict(zip(['tenant_id', 'name', 'llm_id', 'embd_id', 
                          'asr_id', 'img2txt_id', 'role'], row)) 
                for row in results]
    
    @classmethod
    @session_context
    def decrease(cls, session: Session, tenant_id: str, num: int):
        """Decrease a tenant's credit.
        
        Args:
            session: SQLAlchemy session
            tenant_id: Tenant's ID
            num: Amount to decrease
            
        Raises:
            LookupError: If tenant not found
        """
        tenant = session.query(cls.model_class).filter(
            cls.model_class.id == tenant_id).first()
            
        if not tenant:
            raise LookupError("Tenant not found which is supposed to be there")
            
        tenant.credit -= num
    
    @classmethod
    def user_gateway(cls, tenant_id: str):
        """Determine the MINIO gateway for a tenant.
        
        Args:
            tenant_id: Tenant's ID
            
        Returns:
            Gateway index
        """
        hashobj = hashlib.sha256(tenant_id.encode("utf-8"))
        return int(hashobj.hexdigest(), 16) % len(MINIO)


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
    def get_by_tenant_id(cls, session: Session, tenant_id: str):
        """Get all users associated with a tenant.
        
        Args:
            session: SQLAlchemy session
            tenant_id: Tenant's ID
            
        Returns:
            List of user information dictionaries
        """
        results = session.query(
            cls.model_class.user_id,
            cls.model_class.status,
            cls.model_class.role,
            User.nickname,
            User.email,
            User.avatar,
            User.is_authenticated
        ).join(
            User, 
            cls.model_class.user_id == User.id
        ).filter(
            cls.model_class.tenant_id == tenant_id
        ).all()
        
        # Convert results to dictionaries
        return [dict(zip(['user_id', 'status', 'role', 'nickname', 
                          'email', 'avatar', 'is_authenticated'], row)) 
                for row in results]
    
    @classmethod
    @session_context
    def get_tenants_by_user_id(cls, session: Session, user_id: str):
        """Get all tenants associated with a user.
        
        Args:
            session: SQLAlchemy session
            user_id: User's ID
            
        Returns:
            List of tenant information dictionaries
        """
        results = session.query(
            cls.model_class.tenant_id,
            cls.model_class.role,
            Tenant.name,
            Tenant.llm_id,
            Tenant.embd_id
        ).join(
            Tenant, 
            cls.model_class.tenant_id == Tenant.id
        ).filter(
            cls.model_class.user_id == user_id,
            cls.model_class.status == StatusEnum.VALID.value,
            Tenant.status == StatusEnum.VALID.value
        ).all()
        
        # Convert results to dictionaries
        return [dict(zip(['tenant_id', 'role', 'name', 'llm_id', 'embd_id'], row)) 
                for row in results] 