"""
Unit tests for Username Registration & Alternative ID Recommendation feature.
Executes purely in Python with zero Web framework or real DB connections.
"""
import pytest
from domain import validate_username, InvalidUsernameError
from ports import UserRepositoryPort, UsernameSuggesterPort
from adapters import InMemoryUserRepository, RuleBasedUsernameSuggester
from application import RegisterUsernameUseCase

def test_invalid_username_format_rejection():
    # 1. Short username (< 4 chars)
    with pytest.raises(InvalidUsernameError) as exc_info:
        validate_username("abc")
    assert "4 到 20 個字元" in str(exc_info.value)

    # 2. Long username (> 20 chars)
    with pytest.raises(InvalidUsernameError) as exc_info:
        validate_username("a" * 21)
    assert "4 到 20 個字元" in str(exc_info.value)

    # 3. Invalid special characters
    with pytest.raises(InvalidUsernameError) as exc_info:
        validate_username("user@name")
    assert "英文字母、數字與底線" in str(exc_info.value)

    with pytest.raises(InvalidUsernameError) as exc_info:
        validate_username("user-name")
    assert "英文字母、數字與底線" in str(exc_info.value)

    # 4. Reserved words blocklist
    with pytest.raises(InvalidUsernameError) as exc_info:
        validate_username("admin")
    assert "系統保留字" in str(exc_info.value)

    with pytest.raises(InvalidUsernameError) as exc_info:
        validate_username("ROOT")
    assert "系統保留字" in str(exc_info.value)

def test_successful_username_registration():
    repo = InMemoryUserRepository()
    suggester = RuleBasedUsernameSuggester()
    use_case = RegisterUsernameUseCase(repo, suggester)

    result = use_case.execute("cpbl_fan")
    assert result["success"] is True
    assert result["registered_username"] == "cpbl_fan"
    assert repo.exists_by_username("cpbl_fan") is True

def test_duplicate_username_triggers_validation_boundary_recommendations():
    # Pre-populate repo with 'cpbl_fan' and its first candidate 'cpbl_fan2026'
    repo = InMemoryUserRepository(initial_usernames=["cpbl_fan", "cpbl_fan2026"])
    suggester = RuleBasedUsernameSuggester()
    use_case = RegisterUsernameUseCase(repo, suggester)

    result = use_case.execute("cpbl_fan")
    
    assert result["success"] is False
    assert result["reason"] == "taken"
    
    recommendations = result["recommendations"]
    assert len(recommendations) == 3

    # Verify Validation Boundary guarantees:
    # 1. 'cpbl_fan2026' was filtered out because it is already taken.
    assert "cpbl_fan2026" not in recommendations

    # 2. Every returned candidate passes domain validation and is NOT in DB
    for rec in recommendations:
        assert validate_username(rec) is True
        assert repo.exists_by_username(rec) is False
