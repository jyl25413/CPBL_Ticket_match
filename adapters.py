"""
Adapters implementation for CPBL Ticket Match System.
Provides concrete implementations of Ports using SQLAlchemy and Console logging.
"""
from typing import Optional, Any, Set, List, Dict
from ports import UserRepository, EmailService, UserRepositoryPort, UsernameSuggesterPort
from domain import User as DomainUser
from models import db, User as OrmUser

class SqlAlchemyUserRepository(UserRepository):
    def _to_domain(self, orm_user: Optional[OrmUser]) -> Optional[DomainUser]:
        if not orm_user:
            return None
        return DomainUser(
            id=orm_user.id,
            username=orm_user.username,
            email=orm_user.email,
            password_hash=orm_user.password_hash,
            social_link=orm_user.social_link
        )

    def get_by_email(self, email: str) -> Optional[DomainUser]:
        if not email:
            return None
        norm_email = email.strip().lower()
        orm_user = OrmUser.query.filter_by(email=norm_email).first()
        return self._to_domain(orm_user)

    def get_by_username(self, username: str) -> Optional[DomainUser]:
        if not username:
            return None
        norm_username = username.strip()
        orm_user = OrmUser.query.filter_by(username=norm_username).first()
        return self._to_domain(orm_user)

    def exists_by_username(self, username: str) -> bool:
        if not username:
            return False
        return OrmUser.query.filter_by(username=username.strip()).first() is not None

    def save(self, user: Any, email: str = "", social_link: str = "", password: str = "") -> DomainUser:
        if isinstance(user, DomainUser):
            d_user = user
        elif hasattr(user, 'username') and hasattr(user, 'email') and not isinstance(user, str):
            d_user = DomainUser(
                username=user.username,
                email=user.email,
                password_hash=getattr(user, 'password_hash', 'hash'),
                social_link=getattr(user, 'social_link', '')
            )
        elif isinstance(user, str):
            from werkzeug.security import generate_password_hash
            d_user = DomainUser(
                username=user,
                email=email,
                password_hash=generate_password_hash(password) if password else "hash",
                social_link=social_link
            )
        else:
            raise TypeError(f"Unsupported type for user: {type(user)}")

        orm_user = OrmUser.query.filter_by(username=d_user.username).first()
        if not orm_user:
            orm_user = OrmUser(
                username=d_user.username,
                email=d_user.email,
                social_link=d_user.social_link,
                password_hash=d_user.password_hash
            )
            db.session.add(orm_user)
        else:
            orm_user.email = d_user.email
            orm_user.social_link = d_user.social_link
            orm_user.password_hash = d_user.password_hash

        db.session.commit()
        return self._to_domain(orm_user)

class ConsoleEmailService(EmailService):
    def send_welcome_email(self, email: str, username: str) -> bool:
        print(f"[EmailService] Sent welcome email to {email} for user '{username}'.")
        return True

class InMemoryUserRepository(UserRepository):
    def __init__(self, initial_usernames: Optional[List[Any]] = None):
        self._users: Dict[str, DomainUser] = {}
        if initial_usernames:
            for u in initial_usernames:
                if isinstance(u, str):
                    self._users[u] = DomainUser(username=u, email=f"{u}@example.com", password_hash="hash")
                elif isinstance(u, DomainUser) or hasattr(u, 'username'):
                    self._users[u.username] = u

    def get_by_username(self, username: str) -> Optional[DomainUser]:
        if not username:
            return None
        return self._users.get(username)

    def exists_by_username(self, username: str) -> bool:
        if not username:
            return False
        return username in self._users

    def get_by_email(self, email: str) -> Optional[DomainUser]:
        if not email:
            return None
        norm = email.strip().lower()
        for u in self._users.values():
            if u.email.lower() == norm:
                return u
        return None

    def save(self, user: Any, email: str = "", social_link: str = "", password: str = "") -> DomainUser:
        if isinstance(user, DomainUser):
            d_user = user
        elif hasattr(user, 'username') and hasattr(user, 'email') and not isinstance(user, str):
            d_user = DomainUser(
                username=user.username,
                email=user.email,
                password_hash=getattr(user, 'password_hash', 'hash'),
                social_link=getattr(user, 'social_link', '')
            )
        elif isinstance(user, str):
            d_user = DomainUser(
                username=user,
                email=email,
                password_hash=password or "hash",
                social_link=social_link
            )
        else:
            raise TypeError(f"Invalid user argument: {type(user)}")

        self._users[d_user.username] = d_user
        return d_user

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
