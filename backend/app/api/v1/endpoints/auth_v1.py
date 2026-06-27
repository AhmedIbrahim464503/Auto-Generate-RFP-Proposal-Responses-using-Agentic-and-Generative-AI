from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from backend.app.core.security.auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    TokenData,
    get_password_hash
)

router = APIRouter()

class LoginRequest(BaseModel):
  username: str
  password: str

class TokenResponse(BaseModel):
  access_token: str
  refresh_token: str
  token_type: str = "bearer"
  role: str

class RefreshRequest(BaseModel):
  refresh_token: str

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
  # Standard mockup login logic for enterprise deployment
  if payload.username == "admin" and payload.password == "admin123":
    claims = {
        "sub": payload.username,
        "role": "Admin",
        "permissions": ["read", "write", "admin", "export"]
    }
  elif payload.username == "writer" and payload.password == "writer123":
    claims = {
        "sub": payload.username,
        "role": "Writer",
        "permissions": ["read", "write"]
    }
  else:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password"
    )

  access_token = create_access_token(data=claims)
  refresh_token = create_refresh_token(data={"sub": payload.username})
  return TokenResponse(
      access_token=access_token,
      refresh_token=refresh_token,
      role=claims["role"]
  )

@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest):
  try:
    # Decode refresh token
    import jwt
    from backend.app.core.security.auth import SECRET_KEY, ALGORITHM
    data = jwt.decode(payload.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    if not data.get("refresh"):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    username = data.get("sub")
    # Resolve roles
    role = "Admin" if username == "admin" else "Writer"
    permissions = ["read", "write", "admin", "export"] if role == "Admin" else ["read", "write"]
    new_access = create_access_token(data={"sub": username, "role": role, "permissions": permissions})
    new_refresh = create_refresh_token(data={"sub": username})
    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        role=role
    )
  except jwt.PyJWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

@router.get("/me", response_model=TokenData)
def get_me(user: TokenData = Depends(get_current_user)):
  return user
