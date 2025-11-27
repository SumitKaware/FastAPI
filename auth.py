# auth.py
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

# --- JWT Configuration (Ideally from Environment Variables) ---
SECRET_KEY = "YOUR_SUPER_SECURE_SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# --- OAuth2 Scheme ---
# This tells FastAPI to look for an Authorization: Bearer <token> header.
# It points to the URL where the client should POST username/password to get a token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Pydantic Models for JWT Payload ---
class Token(BaseModel):
    # This is what we return on successful login
    access_token: str
    token_type: str

class TokenData(BaseModel):
    # This is what we put into the token's payload
    username: str | None = None

# --- JWT Creation and Verification Functions ---

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire.isoformat()}) # Add expiration claim
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        # 1. Decode and verify the JWT signature and expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. Extract the subject (username)
        username: str = payload.get("sub") 
        if username is None:
            raise CREDENTIALS_EXCEPTION
        
        token_data = TokenData(username=username)

    except JWTError:
        # Handles expired or invalid signature
        raise CREDENTIALS_EXCEPTION
    
    # 3. In a real app, you would look up the user in a DB here
    # For now, we return the user data from the token payload
    return {"username": token_data.username}