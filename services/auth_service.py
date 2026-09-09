"""REPRIGHT AI - Authentication Service.

Handles secure password hashing using PBKDF2-HMAC-SHA256, user registration,
credential validation, profile updating, and session authorization.
"""

import hashlib
import hmac
import secrets
import re
from typing import Optional, Tuple
from database.models import User
from database.user_repository import UserRepository

# Configuration for PBKDF2-HMAC-SHA256
PBKDF2_ALGORITHM = "sha256"
PBKDF2_ROUNDS = 200_000
SALT_SIZE_BYTES = 16

VALID_FITNESS_GOALS = [
    "GENERAL_FITNESS",
    "STRENGTH",
    "HYPERTROPHY",
    "ENDURANCE",
    "MOBILITY",
    "REHABILITATION"
]


def hash_password(password: str) -> str:
    """Hashes a plaintext password using PBKDF2-HMAC-SHA256 with a secure random salt."""
    salt = secrets.token_bytes(SALT_SIZE_BYTES)
    key = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        password.encode("utf-8"),
        salt,
        PBKDF2_ROUNDS
    )
    return f"pbkdf2_{PBKDF2_ALGORITHM}${PBKDF2_ROUNDS}${salt.hex()}${key.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verifies a plaintext password against a stored PBKDF2 hash using constant-time comparison."""
    try:
        parts = hashed.split("$")
        if len(parts) != 4:
            return False
        algo, rounds_str, salt_hex, expected_hex = parts
        if not algo.startswith("pbkdf2_"):
            return False
        rounds = int(rounds_str)
        salt = bytes.fromhex(salt_hex)

        key = hashlib.pbkdf2_hmac(
            PBKDF2_ALGORITHM,
            password.encode("utf-8"),
            salt,
            rounds
        )
        return hmac.compare_digest(key.hex(), expected_hex)
    except Exception:
        return False


COMMON_DOMAIN_TYPOS = {
    "gmai.com": "gmail.com",
    "gamil.com": "gmail.com",
    "gmial.com": "gmail.com",
    "gmaill.com": "gmail.com",
    "gmaul.com": "gmail.com",
    "gmaik.com": "gmail.com",
    "yaho.com": "yahoo.com",
    "yahooo.com": "yahoo.com",
    "hotmial.com": "hotmail.com",
    "hotmaill.com": "hotmail.com",
    "outlok.com": "outlook.com",
    "outloo.com": "outlook.com",
}


def check_email_format(email: str) -> Tuple[bool, str]:
    """Validates email format and detects common domain typos."""
    if not email or "@" not in email:
        return False, "Please enter a valid email address (e.g. athlete@example.com)."
    clean = email.strip().lower()
    pattern = r"^[\w\.\+\-]+@[\w\-]+(\.[\w\-]+)+$"
    if not re.match(pattern, clean):
        return False, "Please enter a valid email address (e.g. athlete@example.com)."

    parts = clean.split("@")
    if len(parts) == 2:
        domain = parts[1]
        if domain in COMMON_DOMAIN_TYPOS:
            suggested = COMMON_DOMAIN_TYPOS[domain]
            return False, f"Invalid email domain '@{domain}'. Did you mean '@{suggested}'?"
        tld = domain.split(".")[-1]
        if len(tld) < 2:
            return False, "Invalid email domain extension."

    return True, ""


def validate_email(email: str) -> bool:
    """Performs basic email format validation."""
    valid, _ = check_email_format(email)
    return valid


class AuthService:
    """High-level authentication and user credential lifecycle service."""

    def __init__(self, user_repo: Optional[UserRepository] = None, db_path: Optional[str] = None):
        self.user_repo = user_repo or UserRepository(db_path=db_path)

    def register(
        self,
        name: str,
        email: str,
        password: str,
        height_cm: Optional[float] = None,
        weight_kg: Optional[float] = None,
        fitness_goal: str = "GENERAL_FITNESS"
    ) -> Tuple[bool, str, Optional[User]]:
        """Registers a new athlete with validated credentials and demographic stats."""
        name_clean = name.strip() if name else ""
        email_clean = email.strip().lower() if email else ""

        if not name_clean or len(name_clean) < 2:
            return False, "Full name must be at least 2 characters.", None

        is_valid, email_err = check_email_format(email_clean)
        if not is_valid:
            return False, email_err, None

        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters.", None

        if self.user_repo.get_user_by_email(email_clean) is not None:
            return False, "An account with this email already exists.", None

        goal = fitness_goal.upper() if fitness_goal else "GENERAL_FITNESS"
        if goal not in VALID_FITNESS_GOALS:
            goal = "GENERAL_FITNESS"

        # Validate optional physical metrics
        if height_cm is not None:
            try:
                height_cm = float(height_cm)
                if height_cm <= 0 or height_cm > 260:
                    height_cm = None
            except (ValueError, TypeError):
                height_cm = None

        if weight_kg is not None:
            try:
                weight_kg = float(weight_kg)
                if weight_kg <= 0 or weight_kg > 400:
                    weight_kg = None
            except (ValueError, TypeError):
                weight_kg = None

        pwd_hash = hash_password(password)
        try:
            user = self.user_repo.create_user(
                name=name_clean,
                email=email_clean,
                password_hash=pwd_hash,
                height_cm=height_cm,
                weight_kg=weight_kg,
                fitness_goal=goal
            )
            return True, "Account registered successfully.", user
        except Exception as e:
            return False, f"Registration failed: {e}", None

    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """Authenticates user credentials."""
        email_clean = email.strip().lower() if email else ""
        if not email_clean or not password:
            return False, "Email and password are required.", None

        user = self.user_repo.get_user_by_email(email_clean)
        if not user:
            return False, "Invalid email or password.", None

        if not verify_password(password, user.password_hash):
            return False, "Invalid email or password.", None

        return True, "Login successful.", user

    def update_profile(
        self,
        user_id: int,
        name: str,
        height_cm: Optional[float],
        weight_kg: Optional[float],
        fitness_goal: str
    ) -> Tuple[bool, str, Optional[User]]:
        """Updates user profile information."""
        name_clean = name.strip() if name else ""
        if not name_clean or len(name_clean) < 2:
            return False, "Name must be at least 2 characters.", None

        goal = fitness_goal.upper() if fitness_goal else "GENERAL_FITNESS"
        if goal not in VALID_FITNESS_GOALS:
            goal = "GENERAL_FITNESS"

        success = self.user_repo.update_profile(
            user_id=user_id,
            name=name_clean,
            height_cm=height_cm,
            weight_kg=weight_kg,
            fitness_goal=goal
        )
        if not success:
            return False, "Unable to update profile record.", None

        updated_user = self.user_repo.get_user_by_id(user_id)
        return True, "Profile updated successfully.", updated_user
