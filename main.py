# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta
from auth import oauth2_scheme, get_current_user, create_access_token, Token

app = FastAPI()

# Placeholder for user authentication (replace with DB check and password hashing)
def authenticate_user(username: str, password: str):
    if username == "johndoe" and password == "secret":
        return True
    return False

# --- 1. Login Endpoint (POST /token) ---
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Handles username/password submission and returns an Access Token.
    """
    # 1. Authenticate (Password Flow)
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Create the JWT
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": form_data.username}, # 'sub' is the standard subject claim
        expires_delta=access_token_expires
    )
    
    # 3. Return the token in the required OAuth2 format
    return {"access_token": access_token, "token_type": "bearer"}

# --- 2. Protected Endpoint ---
@app.get("/protected")
async def read_protected_data(user: Annotated[dict, Depends(get_current_user)]):
    """
    This endpoint requires a valid JWT in the Authorization: Bearer header.
    """
    data = f"Secret for user: {user['username']}"
    return {"data": data, "user_info": user}