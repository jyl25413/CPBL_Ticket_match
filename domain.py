"""
Domain logic for User Registration.
This module is pure Python with ZERO dependencies on Flask, SQLAlchemy, or databases.
"""
from dataclasses import dataclass, field
import re
from typing import List, Dict, Any, Optional

@dataclass
class UserRegistrationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    email: str = ""
    username: str = ""
    social_link: str = ""
    password: str = ""
    initial_status: str = "active"
    default_rewards: Dict[str, Any] = field(default_factory=lambda: {
        "welcome_bonus_points": 100,
        "free_listing_credits": 3
    })

def validate_and_build_user(
    email: Optional[str] = None,
    password: Optional[str] = None,
    password_confirm: Optional[str] = None,
    username: Optional[str] = None,
    social_link: Optional[str] = None,
    email_exists: bool = False,
    username_exists: bool = False
) -> UserRegistrationResult:
    """
    Validates user registration fields, normalizes data, and determines initial user status and rewards.
    Pure Python validation logic.
    """
    errors: List[str] = []
    
    # 1. Normalize Email
    raw_email = email.strip() if email else ""
    normalized_email = raw_email.lower()
    
    if not normalized_email:
        errors.append("請提供 Email 信箱！")
    elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", normalized_email):
        errors.append("Email 格式不正確！")
    elif email_exists:
        errors.append("此 Email 已被註冊！")
        
    # 2. Normalize Password
    raw_password = password.strip() if password else ""
    if not raw_password:
        errors.append("請提供密碼！")
    elif len(raw_password) < 4:
        errors.append("密碼長度至少需 4 個字元！")
        
    if password_confirm is not None:
        raw_password_confirm = password_confirm.strip() if password_confirm else ""
        if raw_password != raw_password_confirm:
            errors.append("兩次輸入的密碼必須相同！")

    # 3. Normalize Username
    raw_username = username.strip() if username else ""
    if not raw_username and normalized_email and "@" in normalized_email:
        raw_username = normalized_email.split("@")[0]
        
    if username_exists:
        errors.append("此使用者名稱已被使用！")

    # 4. Normalize Social Link
    raw_social_link = social_link.strip() if social_link else ""
    if not raw_social_link and raw_username:
        raw_social_link = f"https://facebook.com/{raw_username}"

    # 5. Build Result
    is_valid = len(errors) == 0
    
    return UserRegistrationResult(
        is_valid=is_valid,
        errors=errors,
        email=normalized_email,
        username=raw_username,
        social_link=raw_social_link,
        password=raw_password,
        initial_status="active",
        default_rewards={
            "welcome_bonus_points": 100,
            "free_listing_credits": 3
        }
    )

class InvalidUsernameError(ValueError):
    """Exception raised when a username fails domain validation rules."""
    pass

RESERVED_USERNAMES = {"admin", "root", "system", "superuser", "moderator", "official"}

def validate_username(username: str) -> bool:
    """
    Validates a username against deterministic domain business rules.
    - Length: 4 to 20 characters
    - Pattern: Alphanumeric and underscores only ([a-zA-Z0-9_])
    - Blocklist: Must not be a system reserved word
    Raises InvalidUsernameError if non-compliant.
    """
    if not username:
        raise InvalidUsernameError("使用者名稱不能為空。")
        
    username_str = str(username).strip()
    
    if len(username_str) < 4 or len(username_str) > 20:
        raise InvalidUsernameError("使用者名稱長度必須介於 4 到 20 個字元之間。")
        
    if not re.match(r"^[a-zA-Z0-9_]+$", username_str):
        raise InvalidUsernameError("使用者名稱只能包含英文字母、數字與底線。")
        
    if username_str.lower() in RESERVED_USERNAMES:
        raise InvalidUsernameError(f"使用者名稱 '{username_str}' 為系統保留字，不得使用。")
        
    return True

