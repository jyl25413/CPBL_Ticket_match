"""
Application Layer Use Cases for CPBL Ticket Match System.
Orchestrates domain validation, user persistence, and external service side-effects.
"""
from typing import Optional, Dict, Any, List
from domain import validate_and_build_user, UserRegistrationResult, validate_username, InvalidUsernameError
from ports import UserRepository, EmailService, UserRepositoryPort, UsernameSuggesterPort

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

class RegisterUsernameUseCase:
    """
    Use Case for registering a username with alternative ID recommendations.
    Employs a strict Validation Boundary to ensure all returned recommendations
    pass both domain format rules and DB availability checks.
    """
    def __init__(self, user_repo: UserRepositoryPort, suggester: UsernameSuggesterPort):
        self.user_repo = user_repo
        self.suggester = suggester

    def execute(self, username: str, limit: int = 3) -> Dict[str, Any]:
        # a. Domain format validation
        validate_username(username)

        # b. Check availability in repository
        if not self.user_repo.exists_by_username(username):
            self.user_repo.save(username)
            return {
                "success": True,
                "registered_username": username
            }

        # c & d. Username is taken -> Generate candidates & apply Validation Boundary
        candidates = self.suggester.suggest(username, limit=limit * 3)
        valid_recommendations: List[str] = []

        for cand in candidates:
            # 1. Domain format check
            try:
                validate_username(cand)
            except InvalidUsernameError:
                continue

            # 2. DB availability check
            if not self.user_repo.exists_by_username(cand) and cand not in valid_recommendations:
                valid_recommendations.append(cand)

            if len(valid_recommendations) >= limit:
                break

        return {
            "success": False,
            "reason": "taken",
            "message": f"使用者名稱 '{username}' 已被使用",
            "recommendations": valid_recommendations
        }

