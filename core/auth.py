import os
from typing import Optional
from google.oauth2 import id_token
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport import requests as grequests
from fastapi import Depends, HTTPException, status, Request
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CLIENT_ID = os.environ.get("CLIENT_ID")

from fastapi import Depends, HTTPException, status, Request
from typing import Optional
import httpx

async def get_current_user(request: Request) -> dict:
    auth_header: Optional[str] = request.headers.get("Authorization")
    print(auth_header)
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="No token provided"
        )

    access_token = auth_header.split(" ")[1]

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )

        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user_info = resp.json()
        return {
            "sub": user_info.get("id"),
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "access_token": access_token,
        }

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"HTTP error: {str(e)}"
        )


def get_google_sheets_service(user: dict = Depends(get_current_user)):
    print(f"User {user['email']} verify successful")
    access_token = user["access_token"]
    creds = Credentials(token=access_token, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)