from fastapi.responses import RedirectResponse
from jose import jwt, jwe
from datetime import datetime, timedelta
from load_var import Config
from config import Key
from fastapi import HTTPException
from Cache_Info.redis_Read import Read
import logging
from Support_master.compress import encrypt, decrypt

logger = logging.getLogger(__name__)

# Security constants

class TokenCreationError(Exception):
    """Custom exception for token creation failures"""
    pass

class MyToken:
    def __init__(self):
        self.private_key, self.public_key, self.key = Key.getkey()
        self.read= Read()

    async def create_access_token(self, data: dict) -> str:
        try:
            expire = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode = data.copy()
            to_encode.update({
                "exp": expire, 
                "iat": datetime.utcnow(),
                "type": "access"
            })
            
            # Create JWS first
            jws = jwt.encode(
                to_encode, 
                self.private_key.to_pem(private_key=True).decode(),
                algorithm=Config.JWT_ALGORITHM,
                headers={"kid": self.key.kid}
            )
            
            # Encrypt JWS to JWE
            encrypted = jwe.encrypt(
                jws.encode('utf-8'),
                self.public_key,
                encryption='A256GCM',
                algorithm='RSA-OAEP-256'
            )
            
            logger.info("✓ Access token created successfully")
            return encrypted.decode('utf-8')
            
        except Exception as e:
            logger.error(f"✗ Access token creation failed: {str(e)}")
            raise TokenCreationError(f"Token creation failed: {str(e)}")

    async def create_refresh_token(self, refesh_data: dict):
        
        try:
            
            # Prepare token data
            refesh_data.update({
                "exp": datetime.utcnow() + timedelta(seconds=Config.REFRESH_TOKEN_EXPIRE_SECONDS),
                "type": "refresh",
                "iat": datetime.utcnow()
            })
            
            # Create JWT token string
            refresh_token = jwt.encode(
                refesh_data,
                Config.SECRET_KEY,
                algorithm=Config.REFRESH_ALGORITHM
            )
            
            # Check if Redis storage succeeded
            return refresh_token, True, "Token created and stored successfully"
            
        except TokenCreationError:
            # Re-raise custom exceptions
            raise
        except ValueError as e:
            logger.error(f"✗ Validation error: {str(e)}")
            raise TokenCreationError(f"Invalid data: {str(e)}")
        except Exception as e:
            logger.error(f"✗ Refresh token creation failed: {str(e)}")
            raise TokenCreationError(f"Refresh token creation failed: {str(e)}")

    async def verify_refresh_token(self, refresh_token: str):
        try:
            # Decode token
            payload = jwt.decode(
                refresh_token, 
                Config.SECRET_KEY,
                algorithms=[Config.REFRESH_ALGORITHM]
            )
            jti = payload.get("jti")
            
            if  not jti:
                logger.warning("✗ Invalid token structure: missing jti")
                raise HTTPException(
                    status_code=403, 
                    detail="Invalid token structure"
                )
            jti = decrypt(jti)
            # Verify with Redis
            success = await self.read.read_access_token(jti)
            
            if not success or success == {}:
                logger.warning(f"✗ Refresh token not found in Redis: {jti}")
                raise HTTPException(
                    status_code=403, 
                    detail="Invalid or expired refresh token"
                )
            
            response = RedirectResponse(url=Config.FRONTEND_URL)
            response.set_cookie(
                key="access_token",
                value=success,
                httponly=True,
                samesite="strict",
                max_age=Config.ACCESS_TOKEN_EXPIRE_MINUTES,
                secure=False  # Set to True in production
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                samesite="strict",
                max_age=Config.REFRESH_TOKEN_EXPIRE_SECONDS,
                secure=False  # Set to True in production
            )
            return response
            
        except jwt.ExpiredSignatureError:
            logger.warning("✗ Refresh token expired")
            raise HTTPException(status_code=403, detail="Refresh token expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"✗ Invalid refresh token: {str(e)}")
            raise HTTPException(status_code=403, detail="Invalid refresh token")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"✗ Token verification error: {str(e)}")
            raise HTTPException(
                status_code=403, 
                detail=f"Token verification failed: {str(e)}"
            )
      

    async def verify_access_token(self, token: str) -> dict:
        try:
            # Decrypt JWE
            decrypted = jwe.decrypt(token.encode('utf-8'), self.private_key)
            
            # Verify JWS
            payload = jwt.decode(
                decrypted.decode('utf-8'),
                self.public_key.to_pem().decode('utf-8'),
                algorithms=[Config.JWT_ALGORITHM]
            )

            logger.info("✓ Access token verified successfully")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("✗ Access token expired")
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"✗ Invalid access token: {str(e)}")
            raise HTTPException(status_code=403, detail="Invalid token")
        except Exception as e:
            logger.error(f"✗ Token verification error: {str(e)}")
            raise HTTPException(
                status_code=403, 
                detail=f"Token verification failed: {str(e)}"
            )