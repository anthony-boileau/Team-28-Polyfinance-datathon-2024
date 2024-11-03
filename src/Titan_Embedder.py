import os
import json
import logging
from typing import Optional, Dict, Any
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import datetime
import uuid
from decimal import Decimal
from singleton_decorator import singleton

load_dotenv('.secrets')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class EmbedError(Exception):
    """Custom exception for errors returned by Amazon Titan Multimodal Embeddings G1"""
    
    def __init__(self, message: str):
        self.message = message

@singleton
class TitanEmbedder:
    """
    Class for generating embeddings using Amazon Titan Multimodal Embeddings G1.
    Decorated with @singleton to ensure only one instance is created.
    """
    logger = logging.getLogger(__name__)

    def __init__(self, 
                 model_id: str = "amazon.titan-embed-text-v1",
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 aws_session_token: Optional[str] = None,
                 aws_region: Optional[str] = None) -> None:
        """
        Initialize the TitanEmbedder with AWS credentials and model ID.
        """
        self.model_id = model_id
        self.aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_session_token = aws_session_token or os.getenv("AWS_SESSION_TOKEN")
        self.aws_region = aws_region or os.getenv("AWS_DEFAULT_REGION")
        
        # Initialize Bedrock and DynamoDB clients
        self.bedrock = self._initialize_bedrock_client()
        self.dynamodb = self._initialize_dynamodb_client()
        self.table_name = 'Titan_EmbedderRetriever_Vector_DB'
        
        self.logger.info("TitanEmbedder initialized with model ID: %s", self.model_id)

    def _initialize_bedrock_client(self) -> boto3.client:
        """Initialize and return the Bedrock Runtime client."""
        return boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.aws_region
        )

    def _initialize_dynamodb_client(self) -> boto3.resource:
        """Initialize and return the DynamoDB resource."""
        return boto3.resource(
            'dynamodb',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.aws_region
        )

    def __getstate__(self) -> dict:
        """Customize object serialization to maintain singleton pattern."""
        return self.__dict__

    def __setstate__(self, state: dict) -> None:
        """Customize object deserialization to maintain singleton pattern."""
        self.__dict__ = state

    def generate_embeddings(self, input_text: str) -> Dict[str, Any]:
        """
        Generate embeddings for the given input text.
        
        Args:
            input_text (str): The text to generate embeddings for
            
        Returns:
            Dict[str, Any]: The response containing the embeddings
            
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
        Insert embedding and its metadata into DynamoDB.
        
        Args:
            embedding (list): The embedding vector to store
            input_text (str): The original input text
            
        Raises:
            EmbedError: If insertion fails
        """
        self.logger.info("Inserting embedding into the database for the input text.")
        
        table = self.dynamodb.Table(self.table_name)
        
        embedding_decimal = [Decimal(str(x)) for x in embedding]  # Convert to Decimal

        item = {
            'embedding_id': str(uuid.uuid4()),  # Unique ID for each embedding
            'timestamp': str(datetime.datetime.now(datetime.timezone.utc)),  # Timestamp in UTC
            'embedding': embedding_decimal,
            'text': input_text
        }

        try:
            table.put_item(Item=item)
            print(f"Inserted embedding for text: {input_text} into the database.")
        
        except ClientError as e:
            error_message = e.response['Error']['Message']
            self.logger.error(f"Failed to insert item into DynamoDB: {error_message}")
            raise EmbedError(f"Failed to insert item: {error_message}")

def main():
    """Main function to demonstrate usage of TitanEmbedder."""
    model_id = "amazon.titan-embed-text-v1"

    embedder = TitanEmbedder(model_id=model_id)
    input_text = "What are the different services that you offer?"

    try:
        response = embedder.generate_embeddings(input_text)
        embedding = response['embedding']
        embedder.insert_embedding_to_db(embedding, input_text)

    except EmbedError as err:
        logger.error(err.message)
        print(err.message)
    else:
        print(f"Finished generating text embeddings with Amazon Titan Multimodal Embeddings G1 model {model_id}.")

if __name__ == "__main__":
    main()