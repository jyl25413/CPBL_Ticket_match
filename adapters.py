"""
Adapters implementation for CPBL Ticket Match System.
Provides concrete implementations of Ports using SQLAlchemy and Console logging.
"""
from typing import Optional, Any, Set, List
from ports import UserRepository, EmailService, UserRepositoryPort, UsernameSuggesterPort
from models import db, User

class SqlAlchemyUserRepository(UserRepository):
    def get_by_email(self, email: str) -> Optional[User]:
        if not email:
            return None
        norm_email = email.strip().lower()
        return User.query.filter_by(email=norm_email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        if not username:
            return None
        norm_username = username.strip()
        return User.query.filter_by(username=norm_username).first()

    def save(self, username: str, email: str, social_link: str, password: str) -> User:
        user = User(
            username=username,
            email=email,
            social_link=social_link
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

class ConsoleEmailService(EmailService):
    def send_welcome_email(self, email: str, username: str) -> bool:
        print(f"[EmailService] Sent welcome email to {email} for user '{username}'.")
        return True

class InMemoryUserRepository(UserRepositoryPort):
    def __init__(self, initial_usernames: Optional[List[str]] = None):
        self._usernames: Set[str] = set(initial_usernames) if initial_usernames else set()

    def exists_by_username(self, username: str) -> bool:
        return username in self._usernames

    def save(self, username: str) -> bool:
        self._usernames.add(username)
        return True

class RuleBasedUsernameSuggester(UsernameSuggesterPort):
    """
    Deterministic rule-based username candidate suggester.
    Generates candidates by appending year, numbers, or suffixes.
    """
    def suggest(self, base_username: str, limit: int = 3) -> List[str]:
        suffixes = ["2026", "_123", "_pro", "_dev", "_vip", "_888", "_001", "_99"]
        candidates = []
        for s in suffixes:
            cand = f"{base_username}{s}"
            candidates.append(cand)
            if len(candidates) >= limit * 3:  # Provide enough candidates for downstream filtering
                break
        return candidates

