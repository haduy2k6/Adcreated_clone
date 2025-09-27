from fastapi import FastAPI, Form, Request, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from typing import Annotated, Optional, List, Dict
import uuid
import json
import bcrypt
import redis.asyncio as redis
from datetime import datetime, timedelta
from jose import jwt, jwe, jwk
from pydantic import BaseModel
import asyncio
from contextlib import asynccontextmanager

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

# Redis connection pool with optimized settings
redis_pool = None

async def get_redis_pool():
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            max_connections=20,  # Connection pooling
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={},
            health_check_interval=30,
        )
    return redis.Redis(connection_pool=redis_pool)

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_pool
    redis_pool = redis.ConnectionPool(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True,
        max_connections=20,
        retry_on_timeout=True,
        socket_keepalive=True,
        health_check_interval=30,
    )
    yield
    # Shutdown
    if redis_pool:
        await redis_pool.aclose()

app = FastAPI(
    title="OAuth Authentication Service", 
    version="1.0.0",
    lifespan=lifespan
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

# Security constants
SECRET_KEY = os.getenv("SECRET_KEY", "winnerRIphone17Macmini24GB1TB1234567890ab").encode()
REFRESH_ALGORITHM = "HS256"
JWT_ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600
REFRESH_TOKEN_EXPIRE_SECONDS = 8 * 24 * 3600  # 8 days
USER_SESSION_EXPIRE_SECONDS = ACCESS_TOKEN_EXPIRE_MINUTES * 15 * 60

# Generate RSA key pair for JWK
key = jwk.RSAKey.generate(kid=str(uuid.uuid4()))
private_key = key
public_key = key.public()

# Optimized Redis operations with async and pipeline
class RedisManager:
    @staticmethod
    async def get_client():
        return await get_redis_pool()
    
    @staticmethod
    async def store_user_data_batch(user_sessions: List[tuple]) -> None:
        """Store multiple user sessions using pipeline for better performance"""
        redis_client = await RedisManager.get_client()
        async with redis_client.pipeline() as pipe:
            for session_id, user_data, expire_time in user_sessions:
                pipe.setex(
                    f"user_session:{session_id}",
                    expire_time,
                    json.dumps(user_data, default=str)
                )
            await pipe.execute()
    
    @staticmethod
    async def store_user_session(session_id: str, user_data: dict) -> None:
        """Store single user session"""
        redis_client = await RedisManager.get_client()
        await redis_client.setex(
            f"user_session:{session_id}",
            USER_SESSION_EXPIRE_SECONDS,
            json.dumps(user_data, default=str)
        )
    
    @staticmethod
    async def get_user_session(session_id: str) -> Optional[dict]:
        """Retrieve user session data"""
        redis_client = await RedisManager.get_client()
        user_data = await redis_client.get(f"user_session:{session_id}")
        if user_data:
            try:
                return json.loads(user_data)
            except json.JSONDecodeError:
                return None
        return None
    
    @staticmethod
    async def store_refresh_token_batch(refresh_tokens: List[tuple]) -> None:
        """Store multiple refresh tokens using pipeline"""
        redis_client = await RedisManager.get_client()
        async with redis_client.pipeline() as pipe:
            for jti, session_id, expire_time in refresh_tokens:
                pipe.setex(f"refresh:{jti}", expire_time, session_id)
            await pipe.execute()
    
    @staticmethod
    async def store_refresh_token(jti: str, session_id: str) -> None:
        """Store single refresh token"""
        redis_client = await RedisManager.get_client()
        await redis_client.setex(f"refresh:{jti}", REFRESH_TOKEN_EXPIRE_SECONDS, session_id)
    
    @staticmethod
    async def get_refresh_token(jti: str) -> Optional[str]:
        """Get refresh token session ID"""
        redis_client = await RedisManager.get_client()
        return await redis_client.get(f"refresh:{jti}")
    
    @staticmethod
    async def check_email_exists(email: str) -> bool:
        """Check if email exists using optimized scan"""
        redis_client = await RedisManager.get_client()
        async for key in redis_client.scan_iter(match="user_session:*", count=100):
            user_data = await redis_client.get(key)
            if user_data:
                try:
                    user_info = json.loads(user_data)
                    if user_info.get("email") == email:
                        return True
                except json.JSONDecodeError:
                    continue
        return False
    
    @staticmethod
    async def find_user_by_email_and_provider(email: str, provider: str) -> tuple:
        """Find user by email and provider, return (user_info, session_id)"""
        redis_client = await RedisManager.get_client()
        async for key in redis_client.scan_iter(match="user_session:*", count=100):
            user_data = await redis_client.get(key)
            if user_data:
                try:
                    user_info = json.loads(user_data)
                    if (user_info.get("email") == email and 
                        user_info.get("provider") == provider):
                        return user_info, user_info.get("session_id")
                except json.JSONDecodeError:
                    continue
        return None, None
    
    @staticmethod
    async def delete_user_session_and_tokens(email: str, session_id: str) -> None:
        """Delete user session and related tokens using pipeline"""
        redis_client = await RedisManager.get_client()
        async with redis_client.pipeline() as pipe:
            # Delete user session
            pipe.delete(f"user_session:{session_id}")
            
            # Find and delete related refresh tokens
            async for key in redis_client.scan_iter(match="refresh:*", count=100):
                stored_session_id = await redis_client.get(key)
                if stored_session_id == session_id:
                    pipe.delete(key)
            
            await pipe.execute()
    
    @staticmethod
    async def health_check() -> bool:
        """Check Redis connection health"""
        try:
            redis_client = await RedisManager.get_client()
            await redis_client.ping()
            return True
        except Exception:
            return False

# Optimized token functions
def create_access_token(data: dict) -> str:
    """Create access token with JWS nested in JWE"""
    try:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = data.copy()
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        # Create JWS first
        jws = jwt.encode(
            to_encode,
            private_key.to_pem(private_key=True).decode(),
            algorithm=JWT_ALGORITHM,
            headers={"kid": key.kid}
        )
        
        # Encrypt JWS to JWE
        encrypted = jwe.encrypt(
            jws.encode('utf-8'),
            public_key,
            encryption='A256GCM',
            algorithm='RSA-OAEP-256'
        )
        return encrypted.decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token creation failed: {str(e)}")

async def create_refresh_token(user_id: str, session_id: str, locations: set = None) -> str:
    """Create refresh token with async Redis storage"""
    try:
        if locations is None:
            locations = set()
        
        jti = str(uuid.uuid4())
        refresh_token = jwt.encode(
            {
                "sub": user_id,
                "session_id": session_id,
                "jti": jti,
                "locations": list(locations),  # Convert set to list for JSON serialization
                "exp": datetime.utcnow() + timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECONDS)
            },
            SECRET_KEY,
            algorithm=REFRESH_ALGORITHM
        )
        
        # Store in Redis asynchronously
        await RedisManager.store_refresh_token(jti, session_id)
        return refresh_token
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh token creation failed: {str(e)}")

async def verify_refresh_token(refresh_token: str):
    """Verify refresh token with async Redis lookup"""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[REFRESH_ALGORITHM])
        user_id = payload.get("sub")
        session_id = payload.get("session_id")
        jti = payload.get("jti")
        
        stored_session_id = await RedisManager.get_refresh_token(jti)
        if not stored_session_id or stored_session_id != session_id:
            raise HTTPException(status_code=403, detail="Invalid refresh token")
        
        locations = set(payload.get("locations", []))
        return user_id, session_id, locations
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

def verify_access_token(token: str) -> dict:
    """Verify access token: Decrypt JWE then verify JWS"""
    try:
        # Decrypt JWE
        decrypted = jwe.decrypt(token.encode('utf-8'), private_key)
        
        # Verify JWS
        payload = jwt.decode(
            decrypted.decode('utf-8'),
            public_key.to_pem().decode('utf-8'),
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Token verification failed: {str(e)}")

# Utility functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

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

    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="http://localhost:5173/login")

    try:
        verify_access_token(token)
        response = await call_next(request)
        return response
    except HTTPException as he:
        if he.status_code == 401:  # Expired token
            refresh_token = request.cookies.get("refresh_token")
            if not refresh_token:
                return RedirectResponse(url="http://localhost:5173/login")

            try:
                user_id, session_id, locations = await verify_refresh_token(refresh_token)
                client_ip = get_client_ip(request)
                
                # Check location limit
                if len(locations) >= 3 and client_ip not in locations:
                    return RedirectResponse(url="http://localhost:5173/login")
                
                # Add current IP to locations
                locations.add(client_ip)
                
                # Create new tokens
                new_access_token = create_access_token(data={"sub": user_id})
                new_refresh_token = await create_refresh_token(user_id, session_id, locations)
                
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
            except Exception:
                return RedirectResponse(url="http://localhost:5173/login")
        else:
            return RedirectResponse(url="http://localhost:5173/login")
    except Exception:
        return RedirectResponse(url="http://localhost:5173/login")

# OAuth configuration
config = Config(
    environ={
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id"),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret"),
        "GOOGLE_SERVER_METADATA_URL": "https://accounts.google.com/.well-known/openid_configuration",
        "FACEBOOK_CLIENT_ID": os.getenv("FACEBOOK_CLIENT_ID", "your-facebook-client-id"),
        "FACEBOOK_CLIENT_SECRET": os.getenv("FACEBOOK_CLIENT_SECRET", "your-facebook-client-secret"),
        "FACEBOOK_SERVER_METADATA_URL": "https://www.facebook.com/.well-known/openid_configuration/",
    }
)

oauth = OAuth(config)

oauth.register(
    name="google",
    client_id=config.environ["GOOGLE_CLIENT_ID"],
    client_secret=config.environ["GOOGLE_CLIENT_SECRET"],
    server_metadata_url=config.environ["GOOGLE_SERVER_METADATA_URL"],
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name="facebook",
    client_id=config.environ["FACEBOOK_CLIENT_ID"],
    client_secret=config.environ["FACEBOOK_CLIENT_SECRET"],
    server_metadata_url=config.environ["FACEBOOK_SERVER_METADATA_URL"],
    client_kwargs={"scope": "email public_profile"},
)

# Routes
@app.get("/")
async def root():
    return {"message": "OAuth Authentication Service", "version": "1.0.0"}

@app.get("/signup/{choose}")
async def signup(request: Request, choose: str):
    try:
        redirect_uri = f"http://localhost:8000/signup/callback/{choose}"
        if choose == "google":
            return await oauth.google.authorize_redirect(request, redirect_uri)
        elif choose == "facebook":
            return await oauth.facebook.authorize_redirect(request, redirect_uri)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth redirect failed: {str(e)}")

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