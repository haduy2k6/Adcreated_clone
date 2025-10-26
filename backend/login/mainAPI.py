import asyncio
from fastapi import FastAPI, Form, Request, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from typing import Annotated, Optional
import uuid
import bcrypt
from pydantic import BaseModel
from Support_master.token import MyToken,REFRESH_TOKEN_EXPIRE_SECONDS,ACCESS_TOKEN_EXPIRE_MINUTES

# Pydantic models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserData(BaseModel):
    session_id: str
    email: str
    name: Optional[str] = None
    username: Optional[str] = None
    picture: Optional[str] = None
    provider: str
    phone: Optional[str] = ""
    ip_address: str
    created_at: str
    login_method: str
    password: Optional[str] = None

app = FastAPI(
    title="OAuth Authentication Service"
)
# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=os.urandom(32).hex())



def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    return request.headers.get("x-forwarded-for", request.client.host)

# Enhanced middleware with async Redis operations
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Bypass authentication for public endpoints
    public_endpoints = ["/", "/signup/", "/signup/callback/", "/login", "/health", "/jwks"]
    if any(request.url.path.startswith(path) for path in public_endpoints):
        return await call_next(request)

    token = await request.cookies.get("access_token")

    if token:
        response = await call_next(request)
        return response

    if not token:
        try:
            await MyToken.verify_access_token(token)
            refresh_token = request.cookies.get("refresh_token")
            if refresh_token:
                user_id, session_id, locations = await MyToken.verify_refresh_token(refresh_token)
                client_ip = get_client_ip(request)
                # Check location limit
                if len(locations) >= 3 and client_ip not in locations:
                    return RedirectResponse(url="http://localhost:5173/login")
                                    # Add current IP to locations
                locations.add(client_ip)
                new_access_token,new_refresh_token = await asyncio.gather( # Create new tokens
                    Token.create_access_token(data={"sub": user_id}),
                    Token.create_refresh_token(user_id, session_id, locations)
                    )
                response = await call_next(request)
                 # Set new cookies
                response.set_cookie(
                        key="access_token",
                        value=new_access_token,
                        httponly=True,
                        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        secure=True,
                        samesite="strict"
                    )
                response.set_cookie(
                        key="refresh_token",
                        value=new_refresh_token,
                        httponly=True,
                        max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
                        secure=True,
                        samesite="strict"
                    )
                return response
        except HTTPException as he:
            return RedirectResponse(url="http://localhost:5173/login")
# Routes
@app.get("/")
async def root():
    return {"message": "OAuth Authentication Service", "version": "1.0.0"}

@app.get("/signup/callback/google")
async def callback_google(request: Request, background_tasks: BackgroundTasks):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_response = await oauth.google.get("userinfo", token=token)
        user_info = user_response.json()

        email = user_info.get('email')
        if await RedisManager.check_email_exists(email):
            raise HTTPException(status_code=400, detail="Email already exists")

        session_id = str(uuid.uuid4())
        user_data = {
            "session_id": session_id,
            "email": email,
            "name": user_info.get('name'),
            "picture": user_info.get('picture'),
            "provider": "google",
            "phone": user_info.get('phone', ''),
            "ip_address": get_client_ip(request),
            "created_at": datetime.utcnow().isoformat(),
            "login_method": "oauth_google"
        }

        # Store user data asynchronously
        background_tasks.add_task(RedisManager.store_user_session, session_id, user_data)

        # Create tokens
        access_token = create_access_token(data={"sub": email})
        refresh_token = await create_refresh_token(email, session_id, {get_client_ip(request)})

        response = RedirectResponse(url="http://localhost:5173")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="strict",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False  # Set to True in production
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="strict",
            max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
            secure=False  # Set to True in production
        )
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google OAuth callback failed: {str(e)}")

@app.get("/signup/callback/facebook")
async def callback_facebook(request: Request, background_tasks: BackgroundTasks):
    try:
        token = await oauth.facebook.authorize_access_token(request)
        user_response = await oauth.facebook.get("me?fields=id,name,email,picture", token=token)
        user_info = user_response.json()

        email = user_info.get('email')
        if await RedisManager.check_email_exists(email):
            raise HTTPException(status_code=400, detail="Email already exists")

        session_id = str(uuid.uuid4())
        user_data = {
            "session_id": session_id,
            "email": email,
            "name": user_info.get('name'),
            "picture": user_info.get('picture', {}).get('data', {}).get('url', ''),
            "provider": "facebook",
            "phone": '',
            "ip_address": get_client_ip(request),
            "created_at": datetime.utcnow().isoformat(),
            "login_method": "oauth_facebook"
        }

        # Store user data asynchronously
        background_tasks.add_task(RedisManager.store_user_session, session_id, user_data)

        # Create tokens
        access_token = create_access_token(data={"sub": email})
        refresh_token = await create_refresh_token(email, session_id, {get_client_ip(request)})

        response = RedirectResponse(url="http://localhost:5173")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="strict",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False  # Set to True in production
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="strict",
            max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
            secure=True
        )
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Facebook OAuth callback failed: {str(e)}")

@app.post("/signup/draft")
async def signup_draft(
    request: Request,
    background_tasks: BackgroundTasks,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    email: Annotated[str, Form()],
    phone: Annotated[str, Form()] = ""
):
    try:
        if await RedisManager.check_email_exists(email):
            raise HTTPException(status_code=400, detail="Email already exists")

        session_id = str(uuid.uuid4())
        hashed_password = hash_password(password)
        user_data = {
            "session_id": session_id,
            "email": email,
            "username": username,
            "password": hashed_password,
            "phone": phone,
            "provider": "draft",
            "ip_address": get_client_ip(request),
            "created_at": datetime.utcnow().isoformat(),
            "login_method": "manual"
        }

        # Store user data asynchronously
        background_tasks.add_task(RedisManager.store_user_session, session_id, user_data)

        # Create tokens
        access_token = create_access_token(data={"sub": email})
        refresh_token = await create_refresh_token(email, session_id, {get_client_ip(request)})

        response = RedirectResponse(url="http://localhost:5173")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="strict",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False  # Set to True in production
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="strict",
            max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
            secure=False  # Set to True in production
        )
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/login")
async def login(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()]
):
    try:
        user_found, session_id = await RedisManager.find_user_by_email_and_provider(email, "draft")
        
        if not user_found or not verify_password(password, user_found.get("password", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create tokens
        access_token = create_access_token(data={"sub": email})
        refresh_token = await create_refresh_token(email, session_id, {get_client_ip(request)})

        response = RedirectResponse(url="http://localhost:5173")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="strict",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=True
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="strict",
            max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
            secure=False  # Set to True in production
        )
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/me")
async def get_current_user(request: Request):
    try:
        access_token = request.cookies.get("access_token")
        if not access_token:
            raise HTTPException(status_code=401, detail="Not authenticated - No token found")
        
        payload = verify_access_token(access_token)
        email = payload.get("sub")
        
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token - No sub")
        
        # Find user session by email
        user_found, session_id = await RedisManager.find_user_by_email_and_provider(email, "draft")
        if not user_found:
            # Try other providers
            for provider in ["google", "facebook"]:
                user_found, session_id = await RedisManager.find_user_by_email_and_provider(email, provider)
                if user_found:
                    break
        
        if not user_found:
            raise HTTPException(status_code=401, detail="Session expired or not found")
        
        # Remove sensitive data
        safe_user_data = user_found.copy()
        if "password" in safe_user_data:
            del safe_user_data["password"]
            
        return {
            "authenticated": True,
            "user": safe_user_data,
            "session": {
                "session_id": session_id,
                "provider": user_found.get("provider"),
                "login_time": user_found.get("created_at")
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        return {
            "authenticated": False,
            "message": "Auto-login not available",
            "error": str(e)
        }

@app.post("/logout")
async def logout(request: Request):
    try:
        access_token = request.cookies.get("access_token")
        if access_token:
            try:
                payload = verify_access_token(access_token)
                email = payload.get("sub")
                if email:
                    # Find and delete user session and tokens
                    user_found, session_id = await RedisManager.find_user_by_email_and_provider(email, "draft")
                    if not user_found:
                        for provider in ["google", "facebook"]:
                            user_found, session_id = await RedisManager.find_user_by_email_and_provider(email, provider)
                            if user_found:
                                break
                    
                    if session_id:
                        await RedisManager.delete_user_session_and_tokens(email, session_id)
            except:
                pass
        
        response = RedirectResponse(url="http://localhost:5173")
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@app.get("/jwks")
async def get_jwks():
    return {"keys": [public_key._asdict()]}

@app.get("/health")
async def health_check():
    redis_status = await RedisManager.health_check()
    return {
        "status": "healthy" if redis_status else "unhealthy",
        "redis": "connected" if redis_status else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }