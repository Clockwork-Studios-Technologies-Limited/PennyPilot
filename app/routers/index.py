from fastapi.responses import RedirectResponse
from fastapi import Request, status
from app.dependencies.auth import IsUserLoggedIn, get_current_user, is_admin
from app.dependencies.session import SessionDep
from . import router


# @router.get("/", response_class=RedirectResponse)
# async def index_view(
#     request: Request,
#     user_logged_in: IsUserLoggedIn,
#     db: SessionDep
# ):
#     if user_logged_in:
#         user = await get_current_user(request, db)

#         if await is_admin(user):
#             return RedirectResponse(
#                 url=request.url_for("admin_home_view"),
#                 status_code=status.HTTP_303_SEE_OTHER
#             )

#         return RedirectResponse(
#             url=request.url_for("dashboard_view"),
#             status_code=status.HTTP_303_SEE_OTHER
#         )

#     return RedirectResponse(
#         url=request.url_for("login_view"),
#         status_code=status.HTTP_303_SEE_OTHER
#     )

@router.get("/", response_class=RedirectResponse)
async def index_view(
    user_logged_in: IsUserLoggedIn,
    request: Request,
    db: SessionDep
):
    if not user_logged_in:
        return RedirectResponse("/login", 303)

    user = await get_current_user(request, db)

    if user.role == "admin":
        return RedirectResponse("/admin/dashboard", 303)

    return RedirectResponse("/dashboard", 303)