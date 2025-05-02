import hashlib
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session

from api.db.sql_service.services.base import BaseService, session_context
from api.db.sql_service.models.models import Tenant, UserTenant
from api.db.sql_service.config import (
    DEFAULT_LLM_ID, 
    DEFAULT_EMBEDDING_MODEL_ID,
    DEFAULT_ASR_MODEL_ID,
    DEFAULT_IMAGE_TO_TEXT_MODEL_ID,
    DEFAULT_RERANK_MODEL_ID,
    DEFAULT_TTS_MODEL_ID,
    DEFAULT_PARSER_IDS
)
from api.db import UserTenantRole, StatusEnum
from rag.settings import MINIO


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
            Tenant instance or None if not found
        """
        return session.query(cls.model_class).join(
            UserTenant, 
            and_(
                cls.model_class.id == UserTenant.tenant_id,
                UserTenant.user_id == user_id,
                UserTenant.status == StatusEnum.VALID.value,
                UserTenant.role == UserTenantRole.OWNER
            )
        ).filter(
            cls.model_class.status == StatusEnum.VALID.value
        ).first()
    
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
        
        # Convert results to dictionaries and add the default model IDs
        tenant_list = []
        for row in results:
            tenant_dict = {
                'tenant_id': row[0],
                'name': row[1],
                'llm_id': DEFAULT_LLM_ID,
                'embd_id': DEFAULT_EMBEDDING_MODEL_ID,
                'asr_id': DEFAULT_ASR_MODEL_ID,
                'img2txt_id': DEFAULT_IMAGE_TO_TEXT_MODEL_ID,
                'role': row[2]
            }
            tenant_list.append(tenant_dict)
            
        return tenant_list
    
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