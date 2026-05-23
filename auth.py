#new my shit
from fastapi import HTTPException , status 
from fastapi import Depends 
from typing import Annotated
from database import get_db 
from sqlalchemy.ext.asyncio import AsyncSession
import models
from sqlalchemy import select




from datetime import UTC,datetime,timedelta
import jwt 
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from config import settings


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")

def hash_password(password :str)->str:
    hash= password_hash.hash(password)
    return hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


#encode — payload + secret → signed token string.encode — payload + secret → signed token string.
#decode — signed token string + secret → payload dict (or error if tampered/expired).

# build payload, add expiry, sign with secret key.
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes,
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )
    return encoded_jwt #return the jwt token string


#
def verify_access_token(token: str) -> str | None:
    """Verify a JWT access token and return the subject (user id) if valid."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")
    






# #verifies access token and returns te user
# async def get_current_use( token: Annotated[str ,Depends(oauth2_scheme)], db: Annotated[AsyncSession , Depends(get_db)]):
#        user_id = verify_access_token(token)
#        if not user_id:
#             raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED , detail= " you are not authourised" ,  
#                                 headers={"WWW-Authenticate": "Bearer"})
#        else:
#             result = await db.execute(select(models.User).where(models.User.id == user_id))
#             user = result.scalars().first()
#             if not user:
#                 raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Not authorized",
#                 headers={"WWW-Authenticate": "Bearer"}
#              )
#             return user
           

