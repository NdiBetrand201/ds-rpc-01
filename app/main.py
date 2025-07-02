from typing import Dict, List, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import schemas and services
from app.models.schemas import QueryRequest, QueryResponse, LoginResponse, UserInfo, HealthCheck
from app.services.auth_service import AuthService
from app.services.rag_service import RAGService

# Initialize FastAPI application
app = FastAPI(title="FinSolve Internal Chatbot API", version="1.0.0")

# Security schemes
http_basic_security = HTTPBasic()
http_bearer_security = HTTPBearer(description="JWT token based authentication")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit frontend; restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
auth_service = AuthService()
rag_service = RAGService()

# Pydantic model for user creation
class UserCreate(BaseModel):
    username: str
    password: str
    role: str

# Dependency for protected routes
async def get_current_active_user(token: HTTPAuthorizationCredentials = Depends(http_bearer_security)) -> UserInfo:
    """
    Decodes and verifies the JWT token from the Authorization: Bearer header.
    Populates the accessible_data field using AuthService.
    """
    user_info_dict = auth_service.verify_token(token.credentials)
    accessible_data = auth_service.get_accessible_departments(user_info_dict["role"])
    return UserInfo(
        username=user_info_dict["username"],
        role=user_info_dict["role"],
        accessible_data=accessible_data
    )

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """
    Root endpoint for the API.
    """
    return {"message": "Welcome to FinSolve Internal Chatbot API", "version": "1.0.0"}

@app.post("/login", response_model=LoginResponse)
async def login(credentials: HTTPBasicCredentials = Depends(http_basic_security)):
    """
    Handles user login using SQLite-based authentication.
    Returns a JWT access token if credentials are valid.
    """
    user_data = auth_service.authenticate_user(credentials.username, credentials.password)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    access_token_expires = timedelta(minutes=60)
    access_token = auth_service.create_token(
        username=user_data["username"],
        role=user_data["role"],
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        username=user_data["username"],
        role=user_data["role"],
        message=f"Welcome {user_data['username']}! You are logged in as {user_data['role']}."
    )

@app.post("/add-user", response_model=dict)
async def add_user(user: UserCreate, current_user: UserInfo = Depends(get_current_active_user)):
    """
    Adds a new user to the SQLite database. Restricted to c-level users.
    """
    if current_user.role != "c-level":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only c-level users can add new users."
        )
    
    success = auth_service.add_user(user.username, user.password, user.role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user.username} already exists."
        )
    
    return {"message": f"User {user.username} added successfully with role {user.role}."}

@app.get("/user/accessible-data", response_model=Dict[str, List[str]])
async def get_user_accessible_data(current_user: UserInfo = Depends(get_current_active_user)):
    """
    Retrieves the list of departments accessible to the authenticated user's role.
    """
    return {"accessible_data": current_user.accessible_data}

@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(
    request: QueryRequest,
    current_user: UserInfo = Depends(get_current_active_user)
):
    """
    Processes a chat query from the user, delegating to RAGService with memory support.
    Requires a valid JWT Bearer token.
    """
    try:
        if not auth_service.can_access_query(current_user.role, request.query):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not have permission to ask this type of question."
            )
        
        response = rag_service.process_query(
            query=request.query,
            user_role=current_user.role,
            username=current_user.username,
            context=request.context
        )
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while processing your query: {str(e)}"
        )

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint for monitoring API status.
    """
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        services={
            "AuthService": "operational",
            "RAGService": "operational"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)