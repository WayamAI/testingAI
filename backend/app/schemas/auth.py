from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str
    organization_id: str


class TokenResponse(BaseModel):
    access_token: str
    user: UserOut
