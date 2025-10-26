import asyncio
import hashlib
from load_var import ConfigVar
from typing import Annotated
import bcrypt
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from Cache_Info.redis_Read import Read
from Cache_Info.redis_Create import Create
from Support_master.token import MyToken
from Support_master.compress import encrypt, decompress_data

router = APIRouter()
c= Create()

async def ultra_short_hash(text, length=8):
        h = hashlib.sha256(text.encode()).hexdigest()
        return h[:length]
# Utility functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

@router.get("/login/draft")
async def loginDraft( 
                    email: Annotated[str, Form()],
                    password: Annotated[str, Form()]):
    try:
        passclient = hash_password(password)
        profile = await Read().read_by_email(email) 
        if profile== {} :
            return RedirectResponse(url=ConfigVar.FRONTEND_URL)
        
        s =  await decompress_data(profile.get("data"))
        # Login
        stored_password = s.get("password") or s.get("provider")
        if not stored_password:
            raise HTTPException(400, "Wrong login method")

        if not verify_password(passclient, stored_password):
            raise HTTPException(401, "Wrong password")
        task2 = asyncio.create_task (MyToken().create_access_token(data={"jti":await encrypt(profile.get("jti")) ,"sub":email,"role":s.get("role")}))
        task3 = asyncio.create_task(MyToken().create_refresh_token({'jti':await encrypt(profile.get("jti")) ,'ttl':5600,'session_id':await encrypt(profile.get("session_id")) }))

        access_token, refresh_token = await asyncio.gather(task2,task3)
        response = RedirectResponse(url=ConfigVar.FRONTEND_URL)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="strict",
            max_age=ConfigVar.ACCESS_TOKEN_EXPIRE_MINUTES,
            secure=False  # Set to True in production
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="strict",
            max_age=ConfigVar.REFRESH_TOKEN_EXPIRE_SECONDS,
            secure=False  # Set to True in production
        )
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    