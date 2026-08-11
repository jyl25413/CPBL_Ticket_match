"""
Application Layer Use Cases for CPBL Ticket Match System.
Orchestrates domain validation, user persistence, and external service side-effects.
"""
from typing import Optional, Dict, Any
from domain import validate_and_build_user, UserRegistrationResult
from ports import UserRepository, EmailService

class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository, email_service: EmailService):
        self.user_repo = user_repo
        self.email_service = email_service

    def execute(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        password_confirm: Optional[str] = None,
        username: Optional[str] = None,
        social_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the user registration workflow.
        """
        # 1. Check duplicate email/username using UserRepository
        norm_email = email.strip().lower() if email else ""
        norm_username = username.strip() if username else ""

        email_exists = bool(norm_email and self.user_repo.get_by_email(norm_email))
        username_exists = bool(norm_username and self.user_repo.get_by_username(norm_username))

        # 2. Invoke Domain validation
        reg_result: UserRegistrationResult = validate_and_build_user(
            email=email,
            password=password,
            password_confirm=password_confirm,
            username=username,
            social_link=social_link,
            email_exists=email_exists,
            username_exists=username_exists
        )

        if not reg_result.is_valid:
            return {
                "success": False,
                "errors": reg_result.errors,
                "user": None
            }

        # 3. Handle auto-suffixing if username was derived automatically
        final_username = reg_result.username
        if not norm_username:
            base_username = final_username
            counter = 1
            while self.user_repo.get_by_username(final_username):
                final_username = f"{base_username}_{counter}"
                counter += 1

        # 4. Save User via Repository
        user = self.user_repo.save(
            username=final_username,
            email=reg_result.email,
            social_link=reg_result.social_link,
            password=reg_result.password
        )

        # 5. Send Welcome / Confirmation Email via EmailService
        self.email_service.send_welcome_email(user.email, user.username)

        return {
            "success": True,
            "errors": [],
            "user": user,
            "initial_status": reg_result.initial_status,
            "default_rewards": reg_result.default_rewards
        }
