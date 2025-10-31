"""
Authentication module for FinDash
Handles user registration, login, password hashing, and session management
"""

import bcrypt
import uuid
from datetime import datetime, timedelta
import streamlit as st
from typing import Optional, Dict, Any
import re

import config


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password as string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash

    Args:
        password: Plain text password to verify
        hashed_password: Bcrypt hash to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """
    Validate email format

    Args:
        email: Email address to validate

    Returns:
        True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"

    return True, ""


def generate_reset_token() -> str:
    """
    Generate a unique reset token

    Returns:
        UUID4 token as string
    """
    return str(uuid.uuid4())


def is_token_valid(token_expiry: str) -> bool:
    """
    Check if a reset token is still valid

    Args:
        token_expiry: Token expiry datetime string

    Returns:
        True if token is valid, False otherwise
    """
    try:
        expiry = datetime.strptime(token_expiry, config.DATETIME_FORMAT)
        return datetime.now() < expiry
    except Exception:
        return False


def init_session_state():
    """
    Initialize session state variables if they don't exist
    """
    if config.SESSION_LOGGED_IN not in st.session_state:
        st.session_state[config.SESSION_LOGGED_IN] = False

    if config.SESSION_USER_ID not in st.session_state:
        st.session_state[config.SESSION_USER_ID] = None

    if config.SESSION_USER_EMAIL not in st.session_state:
        st.session_state[config.SESSION_USER_EMAIL] = None

    if config.SESSION_USER_NAME not in st.session_state:
        st.session_state[config.SESSION_USER_NAME] = None

    if config.SESSION_DATA_CACHE not in st.session_state:
        st.session_state[config.SESSION_DATA_CACHE] = {}

    if config.SESSION_LAST_SYNC not in st.session_state:
        st.session_state[config.SESSION_LAST_SYNC] = None


def login_user(user_id: str, email: str, full_name: str):
    """
    Log in a user by setting session state

    Args:
        user_id: User's UUID
        email: User's email
        full_name: User's full name
    """
    st.session_state[config.SESSION_LOGGED_IN] = True
    st.session_state[config.SESSION_USER_ID] = user_id
    st.session_state[config.SESSION_USER_EMAIL] = email
    st.session_state[config.SESSION_USER_NAME] = full_name


def logout_user():
    """
    Log out the current user by clearing session state
    """
    st.session_state[config.SESSION_LOGGED_IN] = False
    st.session_state[config.SESSION_USER_ID] = None
    st.session_state[config.SESSION_USER_EMAIL] = None
    st.session_state[config.SESSION_USER_NAME] = None
    st.session_state[config.SESSION_DATA_CACHE] = {}
    st.session_state[config.SESSION_LAST_SYNC] = None


def is_logged_in() -> bool:
    """
    Check if user is currently logged in

    Returns:
        True if logged in, False otherwise
    """
    return st.session_state.get(config.SESSION_LOGGED_IN, False)


def get_current_user_id() -> Optional[str]:
    """
    Get the current logged-in user's ID

    Returns:
        User ID if logged in, None otherwise
    """
    return st.session_state.get(config.SESSION_USER_ID)


def get_current_user_email() -> Optional[str]:
    """
    Get the current logged-in user's email

    Returns:
        User email if logged in, None otherwise
    """
    return st.session_state.get(config.SESSION_USER_EMAIL)


def get_current_user_name() -> Optional[str]:
    """
    Get the current logged-in user's name

    Returns:
        User name if logged in, None otherwise
    """
    return st.session_state.get(config.SESSION_USER_NAME)
