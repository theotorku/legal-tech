"""
Authentication and authorization service.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import bcrypt
import jwt
from supabase import Client

from config import get_settings
from exceptions import AuthenticationError, ValidationError
from logger import get_logger
from models.subscription_models import User, UserCreate, UserLogin

logger = get_logger(__name__)
settings = get_settings()


class AuthService:
    """Service for user authentication and authorization."""

    def __init__(self, db_client: Client):
        """
        Initialize auth service.

        Args:
            db_client: Supabase client instance
        """
        self.db = db_client
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24  # 24 hours

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    def _generate_api_key(self) -> str:
        """Generate a secure API key."""
        return f"ca_{secrets.token_urlsafe(32)}"

    def _create_access_token(self, user_id: UUID, email: str) -> str:
        """
        Create JWT access token.

        Args:
            user_id: User ID
            email: User email

        Returns:
            JWT token string
        """
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def register_user(self, user_data: UserCreate) -> tuple[User, str]:
        """
        Register a new user.

        Args:
            user_data: User registration data

        Returns:
            Tuple of (User, access_token)

        Raises:
            ValidationError: If email already exists
        """
        try:
            # Check if user already exists
            existing = self.db.table("users").select("id").eq("email", user_data.email).execute()
            if existing.data:
                raise ValidationError("Email already registered")

            # Hash password and generate API key
            password_hash = self._hash_password(user_data.password)
            api_key = self._generate_api_key()

            # Create user
            user_dict = {
                "email": user_data.email,
                "full_name": user_data.full_name,
                "company_name": user_data.company_name,
                "password_hash": password_hash,
                "api_key": api_key,
                "is_active": True,
                "email_verified": False
            }

            result = self.db.table("users").insert(user_dict).execute()
            if not result.data:
                raise ValidationError("Failed to create user")

            user = User(**result.data[0])
            access_token = self._create_access_token(user.id, user.email)

            logger.info(f"User registered successfully: {user.email}")
            return user, access_token

        except Exception as e:
            logger.error(f"User registration failed: {str(e)}", exc_info=True)
            raise

    async def login_user(self, login_data: UserLogin) -> tuple[User, str]:
        """
        Authenticate user and return access token.

        Args:
            login_data: User login credentials

        Returns:
            Tuple of (User, access_token)

        Raises:
            AuthenticationError: If credentials are invalid
        """
        try:
            # Get user by email
            result = self.db.table("users").select("*").eq("email", login_data.email).execute()
            if not result.data:
                raise AuthenticationError("Invalid email or password")

            user_data = result.data[0]

            # Verify password
            if not self._verify_password(login_data.password, user_data["password_hash"]):
                raise AuthenticationError("Invalid email or password")

            # Check if user is active
            if not user_data.get("is_active", False):
                raise AuthenticationError("Account is inactive")

            user = User(**user_data)
            access_token = self._create_access_token(user.id, user.email)

            logger.info(f"User logged in successfully: {user.email}")
            return user, access_token

        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Login failed: {str(e)}", exc_info=True)
            raise AuthenticationError("Login failed")

    async def verify_token(self, token: str) -> User:
        """
        Verify JWT token and return user.

        Args:
            token: JWT token

        Returns:
            User object

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            if user_id is None:
                raise AuthenticationError("Invalid token")

            # Get user from database
            result = self.db.table("users").select("*").eq("id", user_id).execute()
            if not result.data:
                raise AuthenticationError("User not found")

            user = User(**result.data[0])
            if not user.is_active:
                raise AuthenticationError("Account is inactive")

            return user

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.JWTError:
            raise AuthenticationError("Invalid token")
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}", exc_info=True)
            raise AuthenticationError("Token verification failed")

    async def verify_api_key(self, api_key: str) -> User:
        """
        Verify API key and return user.

        Args:
            api_key: API key

        Returns:
            User object

        Raises:
            AuthenticationError: If API key is invalid
        """
        try:
            result = self.db.table("users").select("*").eq("api_key", api_key).execute()
            if not result.data:
                raise AuthenticationError("Invalid API key")

            user = User(**result.data[0])
            if not user.is_active:
                raise AuthenticationError("Account is inactive")

            return user

        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"API key verification failed: {str(e)}", exc_info=True)
            raise AuthenticationError("API key verification failed")

    async def regenerate_api_key(self, user_id: UUID) -> str:
        """
        Regenerate API key for a user.

        Args:
            user_id: User ID

        Returns:
            New API key

        Raises:
            ValidationError: If user not found
        """
        try:
            new_api_key = self._generate_api_key()

            result = self.db.table("users").update(
                {"api_key": new_api_key}
            ).eq("id", str(user_id)).execute()

            if not result.data:
                raise ValidationError("User not found")

            logger.info(f"API key regenerated for user: {user_id}")
            return new_api_key

        except Exception as e:
            logger.error(f"API key regeneration failed: {str(e)}", exc_info=True)
            raise

