# from app.repositories.user import UserRepository
# from app.utilities.security import encrypt_password, verify_password, create_access_token
# from app.schemas.user import RegularUserCreate
# from typing import Optional

# class AuthService:
#     def __init__(self, user_repo: UserRepository):
#         self.user_repo = user_repo

#     def authenticate_user(self, username: str, password: str) -> Optional[str]:
#         user = self.user_repo.get_by_username(username)
#         if not user or not verify_password(plaintext_password=password, encrypted_password=user.password):
#             return None
#         access_token = create_access_token(data={"sub": f"{user.id}", "role": user.role})
#         return access_token

#     def register_user(self, username: str, email: str, password: str):
#         new_user = RegularUserCreate(
#             username=username, 
#             email=email, 
#             password=encrypt_password(password)
#         )
#         return self.user_repo.create(new_user)

from app.repositories.user import UserRepository
from app.utilities.security import encrypt_password, verify_password, create_access_token
from app.models.user import User, UserRole
from typing import Optional


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # -------------------------
    # REGISTER
    # -------------------------
    def register_user(self, username: str, email: str, password: str, role: UserRole):
        hashed_pw = encrypt_password(password)

        user = User(
            username=username,
            email=email,
            hashed_password=hashed_pw,
            role=role
        )

        return self.user_repo.create(user)

    # -------------------------
    # AUTHENTICATE
    # -------------------------
    def authenticate(self, username: str, password: str):
        user = self.user_repo.get_by_username(username)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user
    
    def authenticate_user(self, username: str, password: str):
        user = self.user_repo.get_by_username(username)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    # -------------------------
    # LOGIN (TOKEN CREATION)
    # -------------------------
    # def login_user(self, username: str, password: str):
    #     user = self.authenticate(username, password)

    #     if not user:
    #         return None

    #     token = create_access_token(
    #         data={
    #             "sub": str(user.id),
    #             "role": user.role
    #         }
    #     )

    #     return token
    def login_user(self, username: str, password: str):
        user = self.authenticate_user(username, password)

        if not user:
            return None

        return create_access_token(
            data={
                "sub": str(user.id),
                "role": user.role.value
            }
        )