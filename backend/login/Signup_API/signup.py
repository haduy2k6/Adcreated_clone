import asyncio
from datetime import datetime
from typing import Annotated
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from fastapi import Form, Request,HTTPException
from Support_master.config import OAuthlb
from Cache_Info.redis_Read import Read
from Cache_Info.redis_Create import Create
from snowflake import SnowflakeGenerator
from Support_master.compress import compress_data, encrypt,decrypt,decompress_data
from backend.login.Support_master.token import MyToken
from load_var import ConfigVar
from concurrent.futures import ThreadPoolExecutor

router = APIRouter(tags="Signup router")
google , facebook = OAuthlb.facegle()
r , c = Read(), Create()
__genID = SnowflakeGenerator(instance=40)


@router.get("/signup/{choose}")
async def signup(request: Request, choose: str):
    try:
        redirect_uri = f"http://localhost:8000/signup/callback/{choose}"
        if choose == "google":
            return await google.authorize_redirect(request, redirect_uri)
        elif choose == "facebook":
            return await facebook.authorize_redirect(request, redirect_uri)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth redirect failed: {str(e)}")
    
async def support (jti, session_id, email,data):
    with ThreadPoolExecutor (max_workers= 3 ) as excutor:
        futures = [
            excutor.submit (compress_data, data),
            excutor.submit(encrypt,jti),
            excutor.submit(encrypt, session_id)
        ]
        res = [f.result() for f in futures]
    result = await r.read_by_email(email)
    if result == {}:
        user_data= {
            "jti": jti,
            "session_id": session_id,
            "email":email,
            "data": res[0]
        }
        task1 = asyncio.create_task (c.create_user({
            'session_store':user_data,
            'refresh':{'jti':jti,'ttl':5600,'session_id':session_id, 'role': "normal",'sub':email}
            }))
        task2 = asyncio.create_task (MyToken().create_access_token(data={"jti":res[1] ,"sub":email,"role":"normal"}))
        task3 = asyncio.create_task(MyToken().create_refresh_token({'jti':res[1] ,'ttl':5600,'session_id':res[2] }))
        create_user , access_token, refresh_token = await asyncio.gather(task1,task2,task3)
    else:
        task2 = asyncio.create_task (MyToken().create_access_token(data={"jti":res[1] ,"sub":email,"role":decompress_data(result.get("role"))}))
        task3 = asyncio.create_task(MyToken().create_refresh_token({'jti': res[1] ,'ttl':5600,'session_id':res[2] }))
        access_token, refresh_token = await asyncio.gather(task2,task3)
    return access_token, refresh_token
@router.get("/signup/callback/google")
async def callback_google(request: Request):
    try:
        token = await google.authorize_access_token(request)
        user_response = await google.get("userinfo", token=token)
        user_info = user_response.json()

        email = user_info.get('email')
        
        session_id = next(__genID)
        jti = next(__genID)
        data= {
                                    "name": user_info.get('name'),
                                    "role":"normal",
                                    "picture": user_info.get('picture'),
                                    "provider": "Google2025@",
                                    "phone": user_info.get('phone', ''),
                                    "created_at": datetime.utcnow().isoformat(),
                                    "login_method": "oauth_google"
        }
        result = await support(jti=jti,session_id= session_id, email=email,data=data)
        # Store user data asynchronously
        
        response = RedirectResponse(url=ConfigVar.FRONTEND_URL)
        response.set_cookie(
            key="access_token",
            value=result[0],
            httponly=True,
            samesite="strict",
            max_age=ConfigVar.ACCESS_TOKEN_EXPIRE_MINUTES,
            secure=False  # Set to True in production
        )
        response.set_cookie(
            key="refresh_token",
            value=result[1],
            httponly=True,
            samesite="strict",
            max_age=ConfigVar.REFRESH_TOKEN_EXPIRE_SECONDS,
            secure=False  # Set to True in production
        )
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google OAuth callback failed: {str(e)}")

@router.get("/signup/callback/facebook")
async def callback_facebook(request: Request):
    try:
        token = await facebook.authorize_access_token(request)
        user_response = await facebook.get("me?fields=id,name,email,picture", token=token)
        user_info = user_response.json()

        email = user_info.get('email')
        
        session_id = next(__genID)
        jti = next(__genID)

        data = {     
                "name": user_info.get('name'),
                "role":"normal",
                "picture": user_info.get('picture'),
                "provider": "Facbook2025@",
                "phone": user_info.get('phone', ''),
                "created_at": datetime.utcnow().isoformat(),
                "login_method": "oauth_facebook"
                }
        
        # Store user data asynchronously
        result = await support(jti=jti,session_id= session_id, email=email,data=data)
        # Store user data asynchronously
        
        response = RedirectResponse(url=ConfigVar.FRONTEND_URL)
        response.set_cookie(
            key="access_token",
            value=result[0],
            httponly=True,
            samesite="strict",
            max_age=ConfigVar.ACCESS_TOKEN_EXPIRE_MINUTES,
            secure=False  # Set to True in production
        )
        response.set_cookie(
            key="refresh_token",
            value=result[1],
            httponly=True,
            samesite="strict",
            max_age=ConfigVar.REFRESH_TOKEN_EXPIRE_SECONDS,
            secure=False  # Set to True in production
        )
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Facebook OAuth callback failed: {str(e)}")

@router.post("/signup/draft")
async def signup_draft(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    email: Annotated[str, Form()]
):
    try:
        if await r.read_by_email(email) !={} :
            raise HTTPException(status_code=400, detail="Email already exists")
        session_id = next(__genID)
        jti = next(__genID)
        
        data = {
                            "username": username,
                            "password": password,
                            "phone": "",
                            "picture":"De tim link mac dinh thay the sau",
                            "provider": "draft",
                            "created_at": datetime.utcnow().isoformat(),
                            "login_method": "draft",
                            "role":"normal"
            }
    

        result = await support(jti=jti,session_id= session_id, email=email,data=data)
        # Store user data asynchronously
        
        response = RedirectResponse(url=ConfigVar.FRONTEND_URL)
        response.set_cookie(
            key="access_token",
            value=result[0],
            httponly=True,
            samesite="strict",
            max_age=ConfigVar.ACCESS_TOKEN_EXPIRE_MINUTES,
            secure=False  # Set to True in production
        )
        response.set_cookie(
            key="refresh_token",
            value=result[1],
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
