import boto3
from dotenv import load_dotenv
import os
import time
import chromadb
import asyncio
from chromadb.config import Settings
from singleton_decorator import singleton

# Load environment variables from the .secrets file
load_dotenv('.secrets')

aws_region = os.getenv("AWS_DEFAULT_REGION")
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_session_token = os.getenv("AWS_SESSION_TOKEN")
chroma_client_auth_credentials = os.getenv("CHROMA_CLIENT_AUTH_CREDENTIALS")
chroma_db_ip = os.getenv("CHROMA_DB_IP")

async def connect():
        asynclient = await chromadb.AsyncHttpClient(
            host=chroma_db_ip,
            port=8000,
            settings=Settings(
                chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                chroma_client_auth_credentials=chroma_client_auth_credentials
            )
        )

        return asynclient

    

    
if __name__ == "__main__":
    
    settings=Settings(
                chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                chroma_client_auth_credentials=chroma_client_auth_credentials
    )
    
    client = chromadb.HttpClient(
        host= chroma_db_ip,
        port=8000,
        settings=settings
    )
    
    client.heartbeat()
