from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
import jwt

from app.config import get_settings
from app.repositories.user import UserRepository
from app.services.auth_service import AuthService
from app.dependencies import SessionDep


from fastapi import APIRouter, Form, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from app.dependencies import SessionDep
from app.repositories.user import UserRepository
from app.services.auth_service import AuthService
from app.models.user import UserRole
from app.utilities.flash import flash

router = APIRouter()


# -------------------------
# USER REGISTER
# -------------------------
@router.post("/auth/register")
def user_register(
    request: Request,
    db: SessionDep,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    repo = UserRepository(db)
    auth = AuthService(repo)

    try:
        user = auth.register_user(
            username=username,
            email=email,
            password=password,
            role=UserRole.user
        )
        
        db.add(user)
        db.commit()  # Ensure the user is saved before flashing

        flash(request, "Account created! Please log in.")

        return RedirectResponse("/login", status_code=303)

    except Exception as e:
        flash(request, "User already exists", "danger")
        return RedirectResponse("/register", status_code=303)


# -------------------------
# USER LOGIN
# -------------------------
@router.post("/auth/login")
def user_login(
    request: Request,
    db: SessionDep,
    username: str = Form(...),
    password: str = Form(...)
):
    repo = UserRepository(db)
    auth = AuthService(repo)

    token = auth.login_user(username, password)

    if not token:
        return RedirectResponse("/login", status_code=303)

    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True
    )

    return response

# -------------------------
# ADMIN REGISTER
# -------------------------
@router.post("/auth/admin/register")
def admin_register(
    request: Request,
    db: SessionDep,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    repo = UserRepository(db)
    auth = AuthService(repo)

    try:
        auth.register_user(username, email, password, role=UserRole.admin)

        flash(request, "Admin account created")
        return RedirectResponse("/admin/login", status_code=303)

    except Exception:
        flash(request, "Admin already exists", "danger")
        return RedirectResponse("/admin/register", status_code=303)

# -------------------------
# ADMIN LOGIN
# -------------------------
@router.post("/auth/admin/login")
def admin_login(
    request: Request,
    db: SessionDep,
    username: str = Form(...),
    password: str = Form(...)
):
    repo = UserRepository(db)
    auth = AuthService(repo)

    user = auth.authenticate_user(username, password)

    if not user:
        flash(request, "Invalid credentials", "danger")
        return RedirectResponse("/admin/login", status_code=303)

    if user.role != UserRole.admin:
        flash(request, "Not an admin account", "danger")
        return RedirectResponse("/admin/login", status_code=303)

    token = auth.login_user(username, password)

    response = RedirectResponse("/admin/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True
    )

    return response

# -------------------------
# LOGOUT
# -------------------------
@router.get("/auth/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    
    response.delete_cookie("access_token")

    return response
