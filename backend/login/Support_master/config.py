import asyncio
import uuid
from jose import jwk
from load_var import ConfigVar
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
class Key:
    def get_key():
        key = jwk.RSAKey.generate(kid=str(uuid.uuid4()))
        private_key = key
        public_key = key.public()
        return private_key,public_key,key
    
class Oauthlb:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.config = Config(
            environ={
                "GOOGLE_CLIENT_ID": ConfigVar.GOOGLE_CLIENT_ID,
                "GOOGLE_CLIENT_SECRET": ConfigVar.GOOGLE_CLIENT_SECRET,
                "GOOGLE_SERVER_METADATA_URL": "https://accounts.google.com/.well-known/openid_configuration",
                "FACEBOOK_CLIENT_ID":ConfigVar.FACEBOOK_CLIENT_ID,
                "FACEBOOK_CLIENT_SECRET": ConfigVar.FACEBOOK_CLIENT_SECRET,
                "FACEBOOK_SERVER_METADATA_URL": "https://www.facebook.com/.well-known/openid_configuration/",
            }
        )
        self.oauth = OAuth(self.config)

    async def google(self):
        return await self.oauth.register(
            name="google",
            client_id=self.config.environ["GOOGLE_CLIENT_ID"],
            client_secret=self.config.environ["GOOGLE_CLIENT_SECRET"],
            server_metadata_url=self.config.environ["GOOGLE_SERVER_METADATA_URL"],
            client_kwargs={"scope": "openid email profile"},
        )

    async def facebook(self):
        return await self.oauth.register(
            name="facebook",
            client_id=self.config.environ["FACEBOOK_CLIENT_ID"],
            client_secret=self.config.environ["FACEBOOK_CLIENT_SECRET"],
            server_metadata_url=self.config.environ["FACEBOOK_SERVER_METADATA_URL"],
            client_kwargs={"scope": "email public_profile"},
        )
    async def facegle(self):
        return await asyncio.gather(
        self.oauth.google(),
        self.oauth.facebook()
        )
