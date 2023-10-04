import sys
import os
from typing import Optional

import requests
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jose.constants import ALGORITHMS
from pydantic import BaseModel, BaseSettings

class Settings(BaseSettings):
    app_name: str = "Test Keycloak Auth App"
    public_key: Optional[str] = None
    keycloak_url = os.getenv("KEYCLOAK_URL", "http://localhost:8180")

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str

settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

@app.on_event("startup")
def read_kc_public_key():
    # Why doing this?
    # Because we want to fetch public key on start
    # Later we would verify incoming JWT tokens
    try:
        r = requests.get(settings.keycloak_url + "/auth/realms/master", timeout=3)
        r.raise_for_status()
        response_json = r.json()
        settings.public_key = f'-----BEGIN PUBLIC KEY-----\r\n{response_json["public_key"]}\r\n-----END PUBLIC KEY-----'
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        sys.exit(1)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        sys.exit(1)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        sys.exit(1)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.public_key, algorithms=[ALGORITHMS.RS256],
                             options={"verify_signature": True, "verify_aud": False, "exp": True})
        username: str = payload.get("preferred_username")
        token_data = TokenData(username=username)
    except JWTError as e:
        print(e)
        raise credentials_exception
    return token_data

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]
