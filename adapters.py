"""
Adapters implementation for CPBL Ticket Match System.
Provides concrete implementations of Ports using SQLAlchemy and Console logging.
"""
from typing import Optional, Any
from ports import UserRepository, EmailService
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
