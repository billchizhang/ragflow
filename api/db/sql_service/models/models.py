"""SQLAlchemy models for RAGFlow.

This module provides SQLAlchemy ORM model definitions that combine
the models previously implemented in Peewee and SQLAlchemy.
"""

import os
from datetime import datetime
import json
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, 
    Float, Text, Table, desc, asc, func, Enum
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList as SqlMutableList
from flask_login import UserMixin

from api.db.sql_service.database import Base
from api.db import UserTenantRole, StatusEnum, ParserType, TenantPermission
from api.utils import get_uuid, current_timestamp, datetime_format
from api.db.sql_service.models.fields import JSONType, ListType, SerializedFieldType, MutableJSON, MutableList


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


class User(BaseModel, UserMixin):
    """User model for authentication and profile information.
    
    This model stores user information including authentication details and preferences.
    
    Attributes:
        id (Column): Primary key for the user
        access_token (Column): API access token for the user
        nickname (Column): User's display name
        password (Column): Hashed password for authentication
        email (Column): User's email address (used for login)
        avatar (Column): Base64 encoded avatar image
        language (Column): Preferred language setting
        color_schema (Column): UI color scheme preference
        timezone (Column): User's timezone preference
        last_login_time (Column): Timestamp of last login
        is_authenticated (Column): Flag indicating if user is authenticated
        is_active (Column): Flag indicating if account is active
        is_anonymous (Column): Flag indicating if user is anonymous
        login_channel (Column): Source channel used for login
        status (Column): Account status (1 for active, 0 for inactive)
        is_superuser (Column): Flag indicating administrator privileges
    """
    __tablename__ = "user"

    id = Column(String(32), primary_key=True)
    access_token = Column(String(255), nullable=True, index=True)
    nickname = Column(String(100), nullable=False, index=True)
    password = Column(String(255), nullable=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    avatar = Column(Text, nullable=True)
    language = Column(String(32), nullable=True, default="Chinese" if "zh_CN" in os.getenv("LANG", "") else "English", index=True)
    color_schema = Column(String(32), nullable=True, default="Bright", index=True)
    timezone = Column(String(64), nullable=True, default="UTC+8\tAsia/Shanghai", index=True)
    last_login_time = Column(DateTime, nullable=True, index=True)
    is_authenticated = Column(Boolean, nullable=False, default=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_anonymous = Column(Boolean, nullable=False, default=False, index=True)
    login_channel = Column(String(32), nullable=True, index=True)
    status = Column(String(1), nullable=True, default=StatusEnum.VALID.value, index=True)
    is_superuser = Column(Boolean, nullable=True, default=False, index=True)
    
    # Relationships
    user_tenants = relationship("UserTenant", back_populates="user")
    
    def get_id(self):
        """Return the unique identifier for Flask-Login."""
        return self.id
    
    def __str__(self):
        """String representation of the user."""
        return f"User(id={self.id}, email={self.email})"


class Tenant(BaseModel):
    """Tenant model for multi-tenancy support.
    
    This model stores organization/tenant information for multi-tenant applications.
    
    Attributes:
        id (Column): Primary key for the tenant
        name (Column): Display name of the tenant
        public_key (Column): Public key for API authentication
        llm_id (Column): Default LLM ID for this tenant
        embd_id (Column): Default embedding model ID
        asr_id (Column): Default ASR model ID
        img2txt_id (Column): Default image-to-text model ID
        rerank_id (Column): Default rerank model ID
        tts_id (Column): Default text-to-speech model ID
        parser_ids (Column): Document processor IDs
        credit (Column): Available credits/quota
        status (Column): Tenant status (1 for active, 0 for inactive)
    """
    __tablename__ = "tenant"

    id = Column(String(32), primary_key=True)
    name = Column(String(100), nullable=True, index=True)
    public_key = Column(String(255), nullable=True, index=True)
    
    # Model IDs for various services
    llm_id = Column(String(128), nullable=False, index=True)
    embd_id = Column(String(128), nullable=False, index=True)
    asr_id = Column(String(128), nullable=False, index=True)
    img2txt_id = Column(String(128), nullable=False, index=True)
    rerank_id = Column(String(128), nullable=False, index=True)
    tts_id = Column(String(256), nullable=True, index=True)
    parser_ids = Column(String(256), nullable=False, index=True)
    
    credit = Column(Integer, default=512, index=True)
    status = Column(String(1), nullable=True, default=StatusEnum.VALID.value, index=True)
    
    # Relationships
    user_tenants = relationship("UserTenant", back_populates="tenant")
    knowledgebases = relationship("Knowledgebase", back_populates="tenant")
    
    def __str__(self):
        """String representation of the tenant."""
        return f"Tenant(id={self.id}, name={self.name})"


class UserTenant(BaseModel):
    """User-Tenant association model.
    
    This model represents the many-to-many relationship between users and tenants,
    including role information.
    
    Attributes:
        id (Column): Primary key
        user_id (Column): Foreign key to the user
        tenant_id (Column): Foreign key to the tenant
        role (Column): User's role within the tenant
        invited_by (Column): User ID who invited this user
        status (Column): Status of the association (1 for active, 0 for inactive)
    """
    __tablename__ = "user_tenant"

    id = Column(String(32), primary_key=True)
    user_id = Column(String(32), ForeignKey("user.id"), nullable=False, index=True)
    tenant_id = Column(String(32), ForeignKey("tenant.id"), nullable=False, index=True)
    role = Column(String(32), nullable=False, default=UserTenantRole.NORMAL, index=True)
    invited_by = Column(String(32), nullable=False, index=True)
    status = Column(String(1), nullable=True, default=StatusEnum.VALID.value, index=True)
    
    # Relationships
    user = relationship("User", back_populates="user_tenants")
    tenant = relationship("Tenant", back_populates="user_tenants")
    
    def __str__(self):
        """String representation of the user-tenant association."""
        return f"UserTenant(user_id={self.user_id}, tenant_id={self.tenant_id}, role={self.role})"


class InvitationCode(BaseModel):
    """Invitation code model for user onboarding.
    
    This model stores invitation codes for new users to join tenants.
    
    Attributes:
        id (Column): Primary key
        code (Column): The invitation code itself
        visit_time (Column): When the code was last used
        user_id (Column): User who used the code
        tenant_id (Column): Tenant the user is invited to
        status (Column): Status of the invitation code
    """
    __tablename__ = "invitation_code"
    
    id = Column(String(32), primary_key=True)
    code = Column(String(32), nullable=False, index=True)
    visit_time = Column(DateTime, nullable=True, index=True)
    user_id = Column(String(32), nullable=True, index=True)
    tenant_id = Column(String(32), ForeignKey("tenant.id"), nullable=True, index=True)
    status = Column(String(1), nullable=True, default=StatusEnum.VALID.value, index=True)


class Knowledgebase(BaseModel):
    """Knowledge base model for storing document collections.
    
    This model stores metadata about knowledge bases, which are collections of documents
    used for retrieval and question answering.
    
    Attributes:
        id (Column): Primary key
        avatar (Column): Base64 encoded avatar image
        tenant_id (Column): Foreign key to the tenant
        name (Column): Display name of the knowledge base
        language (Column): Language of the knowledge base
        description (Column): Description of the knowledge base
        embd_id (Column): Embedding model ID
        permission (Column): Access permission (me/team)
        created_by (Column): User ID who created it
        doc_num (Column): Number of documents in the KB
        token_num (Column): Total number of tokens
        chunk_num (Column): Total number of chunks
        similarity_threshold (Column): Threshold for similarity search
        vector_similarity_weight (Column): Weight for vector similarity in hybrid search
        parser_id (Column): Default parser ID
        parser_config (Column): Parser configuration
        pagerank (Column): PageRank score if applicable
        status (Column): Status of the knowledge base
    """
    __tablename__ = "knowledgebase"
    
    id = Column(String(32), primary_key=True)
    avatar = Column(Text, nullable=True)
    tenant_id = Column(String(32), ForeignKey("tenant.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)
    language = Column(String(32), nullable=True, 
                    default="Chinese" if "zh_CN" in os.getenv("LANG", "") else "English", 
                    index=True)
    description = Column(Text, nullable=True)
    embd_id = Column(String(128), nullable=False, index=True)
    permission = Column(String(16), nullable=False, default="me", index=True)
    created_by = Column(String(32), ForeignKey("user.id"), nullable=False, index=True)
    doc_num = Column(Integer, default=0, index=True)
    token_num = Column(Integer, default=0, index=True)
    chunk_num = Column(Integer, default=0, index=True)
    similarity_threshold = Column(Float, default=0.2, index=True)
    vector_similarity_weight = Column(Float, default=0.3, index=True)
    parser_id = Column(String(32), nullable=False, default=ParserType.NAIVE.value, index=True)
    parser_config = Column(JSONType, nullable=False, default={"pages": [[1, 1000000]]})
    pagerank = Column(Integer, default=0)
    status = Column(String(1), nullable=True, default=StatusEnum.VALID.value, index=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="knowledgebases")
    documents = relationship("Document", back_populates="knowledgebase")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __str__(self):
        return self.name


class Document(BaseModel):
    """Document model for storing document metadata.
    
    This model stores information about documents added to knowledge bases,
    including processing status and metadata.
    
    Attributes:
        id (Column): Primary key
        thumbnail (Column): Base64 encoded thumbnail
        kb_id (Column): Foreign key to the knowledge base
        parser_id (Column): Parser ID used for this document
        parser_config (Column): Parser configuration
        source_type (Column): Where the document came from
        type (Column): File extension/type
        created_by (Column): User ID who uploaded it
        name (Column): Document name
        location (Column): Storage location
        size (Column): File size in bytes
        token_num (Column): Number of tokens
        chunk_num (Column): Number of chunks
        progress (Column): Processing progress (0-1)
        progress_msg (Column): Processing message
        process_begin_at (Column): When processing started
        process_duation (Column): Processing duration
        meta_fields (Column): Metadata fields
        run (Column): Processing flag
        status (Column): Document status
    """
    __tablename__ = "document"
    
    id = Column(String(32), primary_key=True)
    thumbnail = Column(Text, nullable=True)
    kb_id = Column(String(32), ForeignKey("knowledgebase.id"), nullable=False, index=True)
    parser_id = Column(String(32), nullable=False, index=True)
    parser_config = Column(JSONType, nullable=False, default={"pages": [[1, 1000000]]})
    source_type = Column(String(128), nullable=False, default="local", index=True)
    type = Column(String(32), nullable=False, index=True)
    created_by = Column(String(32), ForeignKey("user.id"), nullable=False, index=True)
    name = Column(String(255), nullable=True, index=True)
    location = Column(String(255), nullable=True, index=True)
    size = Column(Integer, default=0, index=True)
    token_num = Column(Integer, default=0, index=True)
    chunk_num = Column(Integer, default=0, index=True)
    progress = Column(Float, default=0, index=True)
    progress_msg = Column(Text, nullable=True, default="")
    process_begin_at = Column(DateTime, nullable=True, index=True)
    process_duation = Column(Float, default=0)
    meta_fields = Column(JSONType, nullable=True, default={})
    run = Column(String(1), nullable=True, default="0", index=True)
    status = Column(String(1), nullable=True, default=StatusEnum.VALID.value, index=True)
    
    # Relationships
    knowledgebase = relationship("Knowledgebase", back_populates="documents")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __str__(self):
        return self.name


class File(BaseModel):
    """File model for storing file metadata.
    
    This model stores information about files in the system,
    which may or may not be associated with documents.
    
    Attributes:
        id (Column): Primary key
        parent_id (Column): Parent folder ID
        tenant_id (Column): Tenant ID
        created_by (Column): User who created it
        name (Column): File name
        location (Column): Storage location
        size (Column): File size
        type (Column): File type/extension
        source_type (Column): Source of the file
    """
    __tablename__ = "file"
    
    id = Column(String(32), primary_key=True)
    parent_id = Column(String(32), nullable=False, index=True)
    tenant_id = Column(String(32), ForeignKey("tenant.id"), nullable=False, index=True)
    created_by = Column(String(32), ForeignKey("user.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True, index=True)
    size = Column(Integer, default=0, index=True)
    type = Column(String(32), nullable=False, index=True)
    source_type = Column(String(128), nullable=False, default="", index=True)
    
    # Relationships
    tenant = relationship("Tenant")
    creator = relationship("User", foreign_keys=[created_by])


class File2Document(BaseModel):
    """Association model between files and documents.
    
    This model maps files to documents when a file is processed into a document.
    
    Attributes:
        id (Column): Primary key
        file_id (Column): File ID
        document_id (Column): Document ID
    """
    __tablename__ = "file2document"
    
    id = Column(String(32), primary_key=True)
    file_id = Column(String(32), ForeignKey("file.id"), nullable=True, index=True)
    document_id = Column(String(32), ForeignKey("document.id"), nullable=True, index=True)
    
    # Relationships
    file = relationship("File")
    document = relationship("Document")


class Dialog(BaseModel):
    """Dialog model for storing chat application configurations.
    
    This model stores dialog/chat application settings for RAG applications.
    
    Attributes:
        id (Column): Primary key
        tenant_id (Column): Tenant ID
        name (Column): Dialog name
        description (Column): Dialog description
        icon (Column): Base64 encoded icon
        language (Column): Dialog language
        llm_id (Column): LLM ID
        llm_setting (Column): LLM settings
        prompt_type (Column): Prompt type (simple/advanced)
        prompt_config (Column): Prompt configuration
        similarity_threshold (Column): Similarity threshold
        vector_similarity_weight (Column): Vector similarity weight
        top_n (Column): Top N chunks to retrieve
        top_k (Column): Top K chunks for reranking
        do_refer (Column): Whether to include references
        rerank_id (Column): Reranker model ID
        kb_ids (Column): Knowledge base IDs to use
        status (Column): Dialog status
    """
    __tablename__ = "dialog"
    
    id = Column(String(32), primary_key=True)
    tenant_id = Column(String(32), ForeignKey("tenant.id"), nullable=False, index=True)
    name = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    icon = Column(Text, nullable=True)
    language = Column(String(32), nullable=True, 
                     default="Chinese" if "zh_CN" in os.getenv("LANG", "") else "English", 
                     index=True)
    llm_id = Column(String(128), nullable=False)
    llm_setting = Column(JSONType, nullable=False, 
                        default={"temperature": 0.1, "top_p": 0.3, "frequency_penalty": 0.7,
                                 "presence_penalty": 0.4, "max_tokens": 512})
    prompt_type = Column(String(16), nullable=False, default="simple", index=True)
    prompt_config = Column(JSONType, nullable=False,
                          default={"system": "", "prologue": "Hi! I'm your assistant, what can I do for you?",
                                  "parameters": [],
                                  "empty_response": "Sorry! No relevant content was found in the knowledge base!"})
    similarity_threshold = Column(Float, default=0.2)
    vector_similarity_weight = Column(Float, default=0.3)
    top_n = Column(Integer, default=6)
    top_k = Column(Integer, default=1024)
    do_refer = Column(String(1), nullable=False, default="1")
    rerank_id = Column(String(128), nullable=False)
    kb_ids = Column(JSONType, nullable=False, default=[])
    status = Column(String(1), nullable=True, default=StatusEnum.VALID.value, index=True)
    
    # Relationships
    tenant = relationship("Tenant")
    conversations = relationship("Conversation", back_populates="dialog")


class Conversation(BaseModel):
    """Conversation model for storing chat history.
    
    This model stores conversation history for dialogs.
    
    Attributes:
        id (Column): Primary key
        dialog_id (Column): Dialog ID
        name (Column): Conversation name
        message (Column): Message history
        reference (Column): References used
        user_id (Column): User ID
    """
    __tablename__ = "conversation"
    
    id = Column(String(32), primary_key=True)
    dialog_id = Column(String(32), ForeignKey("dialog.id"), nullable=False, index=True)
    name = Column(String(255), nullable=True, index=True)
    message = Column(JSONType, nullable=True)
    reference = Column(JSONType, nullable=True, default=[])
    user_id = Column(String(32), ForeignKey("user.id"), nullable=True, index=True)
    
    # Relationships
    dialog = relationship("Dialog", back_populates="conversations")
    user = relationship("User") 