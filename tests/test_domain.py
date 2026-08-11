"""
Unit tests for domain.py User Registration logic.
Runs purely in Python without importing Flask or initializing databases.
"""
from domain import UserRegistrationResult, validate_and_build_user

def test_valid_user_registration_defaults():
    result = validate_and_build_user(
        email="  TestUser@Example.com  ",
        password="password123",
        password_confirm="password123"
    )
    
    assert result.is_valid is True
    assert len(result.errors) == 0
    assert result.email == "testuser@example.com"
    assert result.username == "testuser"
    assert result.social_link == "https://facebook.com/testuser"
    assert result.initial_status == "active"
    assert result.default_rewards == {
        "welcome_bonus_points": 100,
        "free_listing_credits": 3
    }

def test_user_registration_explicit_fields():
    result = validate_and_build_user(
        email="User@Domain.com",
        password="MySecretPassword",
        password_confirm="MySecretPassword",
        username="CustomName",
        social_link="https://instagram.com/customname"
    )
    
    assert result.is_valid is True
    assert result.email == "user@domain.com"
    assert result.username == "CustomName"
    assert result.social_link == "https://instagram.com/customname"

def test_invalid_email_format():
    result = validate_and_build_user(
        email="invalid-email-address",
        password="password123"
    )
    
    assert result.is_valid is False
    assert "Email 格式不正確！" in result.errors

def test_missing_required_fields():
    result = validate_and_build_user(
        email="",
        password=""
    )
    
    assert result.is_valid is False
    assert "請提供 Email 信箱！" in result.errors
    assert "請提供密碼！" in result.errors

def test_short_password():
    result = validate_and_build_user(
        email="user@example.com",
        password="123"
    )
    
    assert result.is_valid is False
    assert "密碼長度至少需 4 個字元！" in result.errors

def test_mismatched_password_confirm():
    result = validate_and_build_user(
        email="user@example.com",
        password="password123",
        password_confirm="different_pass"
    )
    
    assert result.is_valid is False
    assert "兩次輸入的密碼必須相同！" in result.errors

def test_duplicate_email_flag():
    result = validate_and_build_user(
        email="existing@example.com",
        password="password123",
        email_exists=True
    )
    
    assert result.is_valid is False
    assert "此 Email 已被註冊！" in result.errors

def test_duplicate_username_flag():
    result = validate_and_build_user(
        email="newuser@example.com",
        password="password123",
        username="existing_user",
        username_exists=True
    )
    
    assert result.is_valid is False
    assert "此使用者名稱已被使用！" in result.errors
