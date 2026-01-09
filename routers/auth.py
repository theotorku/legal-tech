"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from dependencies import get_auth_service
from logger import get_logger
from models.subscription_models import User, UserCreate, UserLogin, UserPublic
from services.auth_service import AuthService

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and receive an access token"
)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user.

    Args:
        user_data: User registration data
        auth_service: Authentication service

    Returns:
        User data and access token
    """
    try:
        user, access_token = await auth_service.register_user(user_data)
        
        return {
            "user": UserPublic(**user.dict()),
            "access_token": access_token,
            "token_type": "bearer",
            "api_key": user.api_key
        }
    
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=dict,
    summary="Login user",
    description="Authenticate user and receive an access token"
)
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login user.

    Args:
        login_data: User login credentials
        auth_service: Authentication service

    Returns:
        User data and access token
    """
    try:
        user, access_token = await auth_service.login_user(login_data)
        
        return {
            "user": UserPublic(**user.dict()),
            "access_token": access_token,
            "token_type": "bearer",
            "api_key": user.api_key
        }
    
    except Exception as e:
        logger.error(f"Login failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get current user",
    description="Get the currently authenticated user's information"
)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get current user information.

    Args:
        credentials: HTTP bearer credentials
        auth_service: Authentication service

    Returns:
        Current user data
    """
    try:
        token = credentials.credentials
        user = await auth_service.verify_token(token)
        return UserPublic(**user.dict())
    
    except Exception as e:
        logger.error(f"Failed to get current user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


@router.post(
    "/regenerate-api-key",
    response_model=dict,
    summary="Regenerate API key",
    description="Generate a new API key for the current user"
)
async def regenerate_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Regenerate API key for current user.

    Args:
        credentials: HTTP bearer credentials
        auth_service: Authentication service

    Returns:
        New API key
    """
    try:
        token = credentials.credentials
        user = await auth_service.verify_token(token)
        new_api_key = await auth_service.regenerate_api_key(user.id)
        
        return {
            "api_key": new_api_key,
            "message": "API key regenerated successfully"
        }
    
    except Exception as e:
        logger.error(f"Failed to regenerate API key: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

