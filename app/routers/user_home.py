from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep, IsUserLoggedIn, get_current_user, is_admin
from . import router, templates


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    return templates.TemplateResponse(
        request=request,
        name="App/dashboard.html",
        context={"user": user}
    )
    
@router.get("/expenses", response_class=HTMLResponse)
async def expenses_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    return templates.TemplateResponse(
        request=request,
        name="App/expenses.html",
        context={"user": user}
    )

@router.get("/subscriptions", response_class=HTMLResponse)
async def subscriptions_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    return templates.TemplateResponse(
        request=request,
        name="App/subscriptions.html",
        context={"user": user}
    )
    
@router.get("/reports", response_class=HTMLResponse)
async def reports_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    return templates.TemplateResponse(
        request=request,
        name="App/reports.html",
        context={"user": user}
    )