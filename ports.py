"""
Ports (Abstract Interfaces) for CPBL Ticket Match System.
Defines abstract contracts for database repositories and external services.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class UserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Any]:
        """Retrieve user entity by email address."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[Any]:
        """Retrieve user entity by username."""
        pass

    @abstractmethod
    def save(self, username: str, email: str, social_link: str, password: str) -> Any:
        """Persist new user entity and return the user object."""
        pass

class EmailService(ABC):
    @abstractmethod
    def send_welcome_email(self, email: str, username: str) -> bool:
        """Send welcome / registration confirmation email."""
        pass
