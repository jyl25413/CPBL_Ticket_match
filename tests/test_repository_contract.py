"""
Repository Contract Tests for UserRepository.
Verifies data persistence, retrieval, and instance isolation without Flask or databases.
"""
import pytest
from domain import User
from adapters import InMemoryUserRepository

def test_new_repository_starts_empty():
    repo = InMemoryUserRepository()
    
    assert repo.get_by_username("nonexistent_user") is None
    assert repo.exists_by_username("nonexistent_user") is False
    assert repo.get_by_email("nonexistent@example.com") is None

def test_save_and_get_user():
    repo = InMemoryUserRepository()
    user = User(
        username="john_doe",
        email="john@example.com",
        password_hash="scrypt:hash123",
        social_link="https://facebook.com/johndoe"
    )
    
    repo.save(user)
    
    # Verify reading back by username
    retrieved = repo.get_by_username("john_doe")
    assert retrieved is not None
    assert retrieved.username == "john_doe"
    assert retrieved.email == "john@example.com"
    assert retrieved.password_hash == "scrypt:hash123"
    assert retrieved.social_link == "https://facebook.com/johndoe"
    
    # Verify exists_by_username
    assert repo.exists_by_username("john_doe") is True
    
    # Verify reading back by email
    retrieved_email = repo.get_by_email("john@example.com")
    assert retrieved_email is not None
    assert retrieved_email.username == "john_doe"

def test_repository_instance_isolation():
    repo1 = InMemoryUserRepository()
    repo2 = InMemoryUserRepository()
    
    user = User(
        username="isolated_user",
        email="isolated@example.com",
        password_hash="hash_iso"
    )
    
    repo1.save(user)
    
    # repo1 contains isolated_user, repo2 MUST NOT contain isolated_user
    assert repo1.exists_by_username("isolated_user") is True
    assert repo2.exists_by_username("isolated_user") is False
    assert repo2.get_by_username("isolated_user") is None
