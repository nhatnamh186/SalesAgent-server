import os
import httpx
from fastapi import APIRouter, Response, Depends
from fastapi.security import OAuth2PasswordBearer

from core.auth import (
    get_current_user,
)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@router.get("/avatar-proxy")
async def proxy_avatar(url: str, user: dict = Depends(get_current_user)):
    print(f"User {user['email']} verify successful")
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return Response(
            content=r.content,
            media_type=r.headers.get("Content-Type", "image/jpeg")
        )
@router.get("/verify-token")
async def proxy_avatar(user: dict = Depends(get_current_user)):
    print(f"User {user['email']} verify successful")