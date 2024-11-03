import os
import json
import logging
from typing import Optional, ClassVar, Dict, Any, List
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from the .secrets file
load_dotenv('.secrets')

class RetrieveError(Exception):
    """Custom exception for errors returned during the retrieval process"""
    
    def __init__(self, message: str):
        self.message = message

class TitanRetriever:
    """
    Singleton class for retrieving similar embeddings using AWS Bedrock.
    Ensures only one instance is created to maintain a single AWS connection.
    """
    # Singleton instance and initialization flag
    _instance: ClassVar[Optional['TitanRetriever']] = None
    _initialized: ClassVar[bool] = False
    
    # Class-level logger
    logger = logging.getLogger(__name__)

    def __new__(cls, *args, **kwargs) -> 'TitanRetriever':
        """
        Create a new instance of TitanRetriever if one doesn't exist.
        Returns the existing instance otherwise.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 aws_session_token: Optional[str] = None,
                 aws_region: Optional[str] = None) -> None:
        """
        Initialize the TitanRetriever with AWS credentials.
        Only runs once even if multiple instances are created.
        
        Args:
            aws_access_key_id (str, optional): AWS Access Key ID
            aws_secret_access_key (str, optional): AWS Secret Access Key
            aws_session_token (str, optional): AWS Session Token
            aws_region (str, optional): AWS Default Region
        """
        # Skip initialization if already initialized
        if TitanRetriever._initialized:
            return
            
        # Use provided credentials or fall back to environment variables
        self.aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_session_token = aws_session_token or os.getenv("AWS_SESSION_TOKEN")
        self.aws_region = aws_region or os.getenv("AWS_DEFAULT_REGION")
        
        # Initialize Bedrock client
        self.bedrock = self._initialize_client()
        self.logger.info("TitanRetriever initialized.")
        
        TitanRetriever._initialized = True
        
    def _initialize_client(self) -> boto3.client:
        """Initialize and return the Bedrock Runtime client."""
        return boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.aws_region
        )

    def retrieve_embedding(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve the top K similar embeddings from the vector database based on the query embedding.
        
        Args:
            query_embedding (List[float]): The embedding vector for the query
            top_k (int): The number of similar embeddings to retrieve
            
        Returns:
            List[Dict[str, Any]]: A list of retrieved embeddings and their corresponding texts
            
        Raises:
            RetrieveError: If retrieval process fails
        """
        self.logger.info("Retrieving top %d embeddings similar to the query.", top_k)
        
        try:
            # Example: Query the vector database for similar embeddings
            # Replace this with actual logic to query your vector database
            # results = db_client.query_similar({"embedding": query_embedding}, top_k=top_k)
            results = [
                {"text": "Sample text 1", "embedding": [0.1, 0.2, 0.3]},
                {"text": "Sample text 2", "embedding": [0.2, 0.1, 0.4]},
                # Add more mock results as needed
            ]
            
            return results[:top_k]
            
        except Exception as e:
            self.logger.error("Error retrieving embeddings: %s", str(e))
            raise RetrieveError("Error retrieving embeddings: " + str(e))

    @classmethod
    def get_instance(cls,
                    aws_access_key_id: Optional[str] = None,
                    aws_secret_access_key: Optional[str] = None,
                    aws_session_token: Optional[str] = None,
                    aws_region: Optional[str] = None) -> 'TitanRetriever':
        """
        Get the singleton instance of the TitanRetriever.
        Creates a new instance if one doesn't exist.
        
        Args:
            aws_access_key_id (str, optional): AWS Access Key ID
            aws_secret_access_key (str, optional): AWS Secret Access Key
            aws_session_token (str, optional): AWS Session Token
            aws_region (str, optional): AWS Default Region
            
        Returns:
            TitanRetriever: The singleton instance
        """
        if cls._instance is None:
            cls._instance = TitanRetriever(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                aws_region=aws_region
            )
        return cls._instance

    def __getstate__(self) -> dict:
        """Customize object serialization to maintain singleton pattern."""
        return self.__dict__

    def __setstate__(self, state: dict) -> None:
        """Customize object deserialization to maintain singleton pattern."""
        self.__dict__ = state
        
def main():
    """
    Entrypoint for the TitanRetriever example.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Initialize AWS credentials and parameters
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    aws_region = os.getenv("AWS_DEFAULT_REGION")

    # Create an instance of TitanRetriever
    retriever = TitanRetriever(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        aws_region=aws_region
    )

    # Example query embedding (this should come from an actual embedding generation process)
    query_embedding = [0.1, 0.2, 0.3]  # Replace with actual embedding vector

    try:
        results = retriever.retrieve_embedding(query_embedding, top_k=3)
        print("Retrieved similar embeddings:")
        for result in results:
            print(f"Text: {result['text']}, Embedding: {result['embedding']}")

    except RetrieveError as err:
        TitanRetriever.logger.error(err.message)
        print(err.message)

    else:
        print("Finished retrieving similar embeddings.")

if __name__ == "__main__":
    main()