from fastapi import APIRouter, HTTPException
from app.schemas.auth import LoginRequest, TokenResponse, UserOut
from app.services.auth_service import login_or_provision, demo_login

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    try:
        token, user = await login_or_provision(payload.email, payload.password)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=token, user=UserOut(**user.model_dump()))


@router.post("/demo-login", response_model=TokenResponse)
async def demo_login_route():
    token, user = await demo_login()
    return TokenResponse(access_token=token, user=UserOut(**user.model_dump()))
