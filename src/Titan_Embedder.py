import os
import json
import logging
from typing import Optional, ClassVar, Dict, Any
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from the .secrets file
load_dotenv('.secrets')

class EmbedError(Exception):
    """Custom exception for errors returned by Amazon Titan Multimodal Embeddings G1"""

    def __init__(self, message: str):
        self.message = message

class TitanEmbedder:
    """
    Singleton class for generating embeddings using Amazon Titan Multimodal Embeddings G1.
    Ensures only one instance is created to maintain a single AWS connection.
    """
    # Singleton instance and initialization flag
    _instance: ClassVar[Optional['TitanEmbedder']] = None
    _initialized: ClassVar[bool] = False
    
    # Class-level logger
    logger = logging.getLogger(__name__)

    def __new__(cls, *args, **kwargs) -> 'TitanEmbedder':
        """
        Create a new instance of TitanEmbedder if one doesn't exist.
        Returns the existing instance otherwise.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, 
                 model_id: str = "amazon.titan-embed-text-v1",
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 aws_session_token: Optional[str] = None,
                 aws_region: Optional[str] = None) -> None:
        """
        Initialize the TitanEmbedder with AWS credentials and model ID.
        Only runs once even if multiple instances are created.
        
        Args:
            model_id (str): The model ID to use
            aws_access_key_id (str, optional): AWS Access Key ID
            aws_secret_access_key (str, optional): AWS Secret Access Key
            aws_session_token (str, optional): AWS Session Token
            aws_region (str, optional): AWS Default Region
        """
        # Skip initialization if already initialized
        if TitanEmbedder._initialized:
            return
            
        # Use provided credentials or fall back to environment variables
        self.model_id = model_id
        self.aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_session_token = aws_session_token or os.getenv("AWS_SESSION_TOKEN")
        self.aws_region = aws_region or os.getenv("AWS_DEFAULT_REGION")
        
        # Initialize Bedrock client
        self.bedrock = self._initialize_client()
        self.logger.info("TitanEmbedder initialized with model ID: %s", self.model_id)
        
        TitanEmbedder._initialized = True
        
    def _initialize_client(self) -> boto3.client:
        """Initialize and return the Bedrock Runtime client."""
        return boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.aws_region
        )

    def generate_embeddings(self, input_text: str) -> Dict[str, Any]:
        """
        Generate a vector of embeddings for a text input using Amazon Titan Multimodal Embeddings G1.
        
        Args:
            input_text (str): The input text to generate embeddings for
            
        Returns:
            Dict[str, Any]: The embeddings, token information, and generation status
            
        Raises:
            EmbedError: If embeddings generation fails
        """
        self.logger.info("Generating embeddings for input text: %s", input_text)

        body = json.dumps({"inputText": input_text})
        accept = "application/json"
        content_type = "application/json"

        try:
            response = self.bedrock.invoke_model(
                body=body, modelId=self.model_id, accept=accept, contentType=content_type
            )

            response_body = json.loads(response.get('body').read())
            finish_reason = response_body.get("message")

            if finish_reason is not None:
                raise EmbedError(f"Embeddings generation error: {finish_reason}")

            return response_body

        except ClientError as err:
            message = err.response["Error"]["Message"]
            self.logger.error("A client error occurred: %s", message)
            raise EmbedError(message)

    def insert_embedding_to_db(self, embedding: list, input_text: str) -> None:
        """
        Insert the generated embeddings into a vector database.
        This is a mock function; implement your actual database insertion logic here.
        
        Args:
            embedding (list): The embedding vector to insert
            input_text (str): The original input text
        """
        self.logger.info("Inserting embedding into the database for the input text.")
        # Example: Adjust according to your vector database's SDK/API
        # db_client.insert({"text": input_text, "embedding": embedding})  # Hypothetical call
        print(f"Inserted embedding for text: {input_text} into the database.")  # Mock print

    @classmethod
    def get_instance(cls, 
                    model_id: str = "amazon.titan-embed-text-v1",
                    aws_access_key_id: Optional[str] = None,
                    aws_secret_access_key: Optional[str] = None,
                    aws_session_token: Optional[str] = None,
                    aws_region: Optional[str] = None) -> 'TitanEmbedder':
        """
        Get the singleton instance of the TitanEmbedder.
        Creates a new instance if one doesn't exist.
        
        Args:
            model_id (str): The model ID to use
            aws_access_key_id (str, optional): AWS Access Key ID
            aws_secret_access_key (str, optional): AWS Secret Access Key
            aws_session_token (str, optional): AWS Session Token
            aws_region (str, optional): AWS Default Region
            
        Returns:
            TitanEmbedder: The singleton instance
        """
        if cls._instance is None:
            cls._instance = TitanEmbedder(
                model_id=model_id,
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

if __name__ == "__main__":
    main()