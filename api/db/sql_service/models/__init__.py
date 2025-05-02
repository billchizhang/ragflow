"""SQLAlchemy models for RAGFlow.

This module provides SQLAlchemy ORM model definitions that combine
the models previously implemented in Peewee and SQLAlchemy.

Classes:
    BaseModel: Base model class with common fields and methods
    User: User model for authentication and profile information
    Tenant: Tenant model for organization/tenant details
    UserTenant: Association model for user-tenant relationships
    Knowledgebase: Knowledge base model for document collections
    Document: Document model for document metadata
    File: File model for file metadata
    File2Document: Association between files and documents
    Dialog: Dialog model for chat applications
    Conversation: Conversation model for chat history
"""

# Import models for convenient access
from api.db.sql_service.models.models import (
    BaseModel, User, Tenant, UserTenant, InvitationCode,
    Knowledgebase, Document, File, File2Document,
    Dialog, Conversation
)
from api.db.sql_service.models.fields import (
    JSONType, ListType, SerializedFieldType, MutableJSON, MutableList
) 