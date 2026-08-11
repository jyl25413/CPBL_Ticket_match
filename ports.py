"""
Ports (Abstract Interfaces) for CPBL Ticket Match System.
Defines abstract contracts for database repositories and external services.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from domain import User

class UserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user entity by email address."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve user entity by username. Returns None if not found."""
        pass

    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        """Check if username exists in repository."""
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        """Persist user entity."""
        pass

class EmailService(ABC):
    @abstractmethod
    def send_welcome_email(self, email: str, username: str) -> bool:
        """Send welcome / registration confirmation email."""
        pass

# Alias for compatibility
UserRepositoryPort = UserRepository

class UsernameSuggesterPort(ABC):
    @abstractmethod
    def suggest(self, base_username: str, limit: int = 3) -> list[str]:
        """Generate a list of recommended alternative usernames."""
        pass

