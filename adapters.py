"""
Adapters implementation for CPBL Ticket Match System.
Provides concrete implementations of Ports using SQLAlchemy and Console logging.
"""
from typing import Optional, Any, Set, List, Dict
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

    def exists_by_username(self, username: str) -> bool:
        if not username:
            return False
        norm_username = username.strip()
        return User.query.filter_by(username=norm_username).first() is not None

    def save(self, username_or_user=None, email: str = None, social_link: str = None, password: str = None, user: User = None, **kwargs) -> User:
        target_user = user or (username_or_user if isinstance(username_or_user, User) else None)
        if target_user is not None:
            db.session.add(target_user)
            db.session.commit()
            return target_user

        uname = username_or_user if isinstance(username_or_user, str) else kwargs.get("username", "user")
        user_obj = User(
            username=uname,
            email=email,
            social_link=social_link
        )
        if password:
            user_obj.set_password(password)
        db.session.add(user_obj)
        db.session.commit()
        return user_obj

class ConsoleEmailService(EmailService):
    def send_welcome_email(self, email: str, username: str) -> bool:
        print(f"[EmailService] Sent welcome email to {email} for user '{username}'.")
        return True

class InMemoryUserRepository(UserRepositoryPort):
    def __init__(self, initial_usernames: Optional[List[str]] = None):
        self._usernames: Set[str] = set(initial_usernames) if initial_usernames else set()
        self._users: Dict[str, User] = {}

    def get_by_email(self, email: str) -> Optional[User]:
        if not email:
            return None
        norm_email = email.strip().lower()
        for u in self._users.values():
            if u.email == norm_email:
                return u
        return None

    def get_by_username(self, username: str) -> Optional[User]:
        if not username:
            return None
        norm = username.strip()
        if norm in self._usernames:
            return self._users.get(norm, User(username=norm, email=f"{norm}@example.com"))
        return self._users.get(norm)

    def exists_by_username(self, username: str) -> bool:
        return username in self._usernames

    def save(self, user_or_username: Any, email: str = "", social_link: str = "", password: str = "") -> User:
        if isinstance(user_or_username, User):
            user_obj = user_or_username
        elif isinstance(user_or_username, str):
            user_obj = User(
                username=user_or_username,
                email=email,
                social_link=social_link
            )
            if password:
                user_obj.set_password(password)
        else:
            raise TypeError(f"Invalid user argument: {type(user_or_username)}")

        self._usernames.add(user_obj.username)
        self._users[user_obj.username] = user_obj
        return user_obj

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
