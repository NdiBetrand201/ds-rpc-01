import jwt
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os
from fastapi import HTTPException, status
from passlib.context import CryptContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    """
    Authentication and authorization service using SQLite for user management.
    Handles user authentication, JWT token creation/verification, and role-based access permissions.
    """

    def __init__(self):
        # Load JWT secret key from environment variable
        self.secret_key = os.getenv("JWT_SECRET_KEY", )
        self.algorithm = "HS256"
        
        # Initialize password hashing context
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Initialize SQLite database
        self.db_path = "data/users.db"
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database and create users and role_permissions tables."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    hashed_password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            """)

            # Create role_permissions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS role_permissions (
                    role TEXT PRIMARY KEY,
                    departments TEXT NOT NULL,
                    data_types TEXT NOT NULL
                )
            """)

            # Seed initial roles and permissions if table is empty
            cursor.execute("SELECT COUNT(*) FROM role_permissions")
            if cursor.fetchone()[0] == 0:
                initial_permissions = [
                    (
                        "finance",
                        "Finance,General",
                        "financial_reports,marketing_expenses,equipment_costs,reimbursements,employee_handbook"
                    ),
                    (
                        "marketing",
                        "Marketing,General",
                        "campaign_performance,customer_feedback,sales_metrics,employee_handbook"
                    ),
                    (
                        "hr",
                        "HR,General",
                        "employee_data,attendance_records,payroll,performance_reviews,employee_handbook"
                    ),
                    (
                        "engineering",
                        "Engineering,General",
                        "technical_architecture,cicd_pipelines,security_models,compliance,employee_handbook"
                    ),
                    (
                        "c-level",
                        "Finance,Marketing,HR,Engineering,General",
                        "all"
                    ),
                    (
                        "employee",
                        "General",
                        "employee_handbook,general_info"
                    )
                ]
                cursor.executemany(
                    "INSERT INTO role_permissions (role, departments, data_types) VALUES (?, ?, ?)",
                    initial_permissions
                )

            # Seed initial users if table is empty
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                initial_users = [
                    ("peter", self.pwd_context.hash("finance123"), "finance"),
                    ("jane", self.pwd_context.hash("marketing456"), "marketing"),
                    ("alice", self.pwd_context.hash("hr789"), "hr"),
                    ("bob", self.pwd_context.hash("eng101"), "engineering"),
                    ("tony", self.pwd_context.hash("exec2023"), "c-level"),
                    ("emma", self.pwd_context.hash("emp303"), "employee")
                ]
                cursor.executemany(
                    "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
                    initial_users
                )

            conn.commit()
            logger.info("SQLite database initialized with users and role_permissions tables.")
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {e}")
            raise
        finally:
            conn.close()

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user by verifying username and password against SQLite database.
        Returns user info (username, role) if valid, else None.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT username, hashed_password, role FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            conn.close()

            if user and self.pwd_context.verify(password, user[1]):
                return {"username": user[0], "role": user[2]}
            logger.warning(f"Authentication failed for username: {username}")
            return None
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return None

    def add_user(self, username: str, password: str, role: str) -> bool:
        """
        Add a new user to the SQLite database with a hashed password.
        Returns True if successful, False if user already exists.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                logger.warning(f"User {username} already exists.")
                conn.close()
                return False

            hashed_password = self.pwd_context.hash(password)
            cursor.execute(
                "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
                (username, hashed_password, role)
            )
            conn.commit()
            logger.info(f"Added user {username} with role {role}.")
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding user {username}: {e}")
            conn.close()
            return False

    def get_accessible_departments(self, role: str) -> List[str]:
        """
        Retrieves the list of department names that a given role is authorized to access from SQLite.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT departments FROM role_permissions WHERE role = ?", (role.lower(),))
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0].split(",")
            logger.warning(f"No permissions found for role: {role}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving departments for role {role}: {e}")
            return []

    def get_accessible_data_types(self, role: str) -> List[str]:
        """
        Retrieves the list of specific data types that a given role is authorized to access from SQLite.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT data_types FROM role_permissions WHERE role = ?", (role.lower(),))
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0].split(",")
            logger.warning(f"No data types found for role: {role}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving data types for role {role}: {e}")
            return []

    def can_access_department(self, role: str, department: str) -> bool:
        """
        Checks if a given role has permission to access data from a specific department.
        Returns True if authorized, False otherwise.
        """
        accessible_departments = self.get_accessible_departments(role)
        return department in accessible_departments or "all" in accessible_departments

    def can_access_data_type(self, role: str, data_type: str) -> bool:
        """
        Checks if a given role has permission to access a specific type of data.
        Returns True if authorized, False otherwise.
        """
        accessible_types = self.get_accessible_data_types(role)
        return data_type in accessible_types or "all" in accessible_types

    def can_access_query(self, role: str, query: str) -> bool:
        """
        Provides a basic level of access control for the query itself.
        Placeholder: Allows all queries, with granular filtering in RAGService.
        """
        return True  # Future: Add NLP-based query analysis for sensitive topics

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verifies a JWT token.
        Returns the decoded payload (user info) if valid.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            role: str = payload.get("role")
            if username is None or role is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload: Missing username or role")
            return {"username": username, "role": role}
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Token verification error: {e}")

    def create_token(self, username: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
        """
        Creates and signs a new JWT token for a given user and role.
        """
        to_encode = {"sub": username, "role": role}
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt