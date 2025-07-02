# models/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QueryRequest(BaseModel):
    """Request model for chat queries"""
    query: str
    context: Optional[str] = None # Added support for optional context in the query

class Source(BaseModel):
    """Source reference model. Represents a document retrieved by the RAG service."""
    document: str # Name or title of the source document
    department: str # Department the document belongs to (e.g., "Finance", "HR")
    update_date: str # Last update date of the document
    relevance_score: float # A score indicating how relevant the document is to the query

class QueryResponse(BaseModel):
    """Response model for chat queries from the API."""
    response: str # The AI's generated response to the query
    sources: List[Source] # List of source documents used to generate the response
    user_role: str # The role of the user who made the query
    timestamp: datetime # Timestamp when the response was generated
    query_processed: str # The actual query string that was processed

class LoginResponse(BaseModel):
    """Response model for the login endpoint."""
    access_token: str # The JWT token for subsequent authenticated requests
    token_type: str # Typically "bearer"
    username: str # The authenticated username
    role: str # The role assigned to the user
    message: str # A custom message for the user

class UserInfo(BaseModel):
    """User information model used internally by FastAPI dependencies."""
    username: str # Username from the JWT token
    role: str # Role from the JWT token
    accessible_data: List[str] # List of data categories (departments) accessible to the user's role

class HealthCheck(BaseModel):
    """Health check response model for API monitoring."""
    status: str # Overall status (e.g., "healthy", "unhealthy")
    timestamp: datetime # Current timestamp of the health check
    services: Dict[str, str] # Dictionary indicating the status of internal services (e.g., "AuthService": "operational")

