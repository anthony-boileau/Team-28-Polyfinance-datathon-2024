import boto3
from dotenv import load_dotenv
import os
import time
import chromadb
import asyncio
from chromadb.config import Settings
from singleton_decorator import singleton

@singleton
class VDB:
    def __init__(self):
        # Initialize the persistent client
        self._client = chromadb.PersistentClient(
            path="./database",
            settings = Settings(allow_reset=True)
            )
    
    def __getattr__(self, name):
        # Delegate any unknown attributes/methods to the client
        return getattr(self._client, name)

def main():

    vdb = VDB()
    # switch `create_collection` to `get_or_create_collection` to avoid creating a new collection every time
    collection = vdb.get_or_create_collection(name="my_collection")
    # switch `add` to `upsert` to avoid adding the same documents every time
    collection.upsert(
        documents=[
            "This is a document about pineapple",
            "This is a document about oranges"
        ],
        ids=["id1", "id2"]
    )
    results = collection.query(
        query_texts=["This is a query document about florida"], # Chroma will embed this for you
        n_results=2 # how many results to return
    )
    print(results)

    vdb.reset()

if __name__ == "__main__":
    main()