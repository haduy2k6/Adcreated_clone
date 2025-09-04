from fastapi import FastAPI
from  authlib.integrations.starlette_client import OAuth
from starlette.config import Config

api= FastAPI()
config = {
    "client_id":"dd",
    "client_url":"we",
    "api_base_url": "https://www.googleapis.com",
    "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration"
}
oauth = OAuth(config)

@app.get("/login/google")
async def loginGg(**args):
    