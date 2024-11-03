import os
import json
import logging
from typing import Optional, Dict, Any, List
import boto3
import numpy as np
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from singleton_decorator import singleton

load_dotenv('.secrets')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class RetrieveError(Exception):
    """Custom exception for errors returned during the retrieval process"""
    
    def __init__(self, message: str):
        self.message = message

@singleton
class TitanRetriever:
    """
    Class for retrieving similar embeddings using AWS Bedrock.
    Decorated with @singleton to ensure only one instance is created.
    """
    logger = logging.getLogger(__name__)

    def __init__(self,
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 aws_session_token: Optional[str] = None,
                 aws_region: Optional[str] = None) -> None:
        """
        Initialize the TitanRetriever with AWS credentials.
        
        Args:
            aws_access_key_id (str, optional): AWS Access Key ID
            aws_secret_access_key (str, optional): AWS Secret Access Key
            aws_session_token (str, optional): AWS Session Token
            aws_region (str, optional): AWS Default Region
        """
        # Use provided credentials or fall back to environment variables
        self.aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_session_token = aws_session_token or os.getenv("AWS_SESSION_TOKEN")
        self.aws_region = aws_region or os.getenv("AWS_DEFAULT_REGION")
        
        # Initialize AWS clients
        self.bedrock = self._initialize_bedrock_client()
        self.dynamodb = self._initialize_dynamodb_client()
        
        self.logger.info("TitanRetriever initialized.")

    def _initialize_bedrock_client(self) -> boto3.client:
        """Initialize and return the Bedrock Runtime client."""
        return boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.aws_region
        )

    def _initialize_dynamodb_client(self) -> boto3.client:
        """Initialize and return the DynamoDB client."""
        return boto3.client(
            service_name='dynamodb',
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

    def calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1 (List[float]): First vector
            vec2 (List[float]): Second vector
            
        Returns:
            float: Cosine similarity score
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def retrieve_embedding(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve the top K similar embeddings from the Titan_EmbedderRetriever_Vector_DB.
        
        Args:
            query_embedding (List[float]): The embedding vector to query with
            top_k (int): Number of similar embeddings to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of similar embeddings with their texts
            
        Raises:
            RetrieveError: If retrieval process fails
        """
        self.logger.info("Retrieving top %d embeddings similar to the query.", top_k)

        try:
            # Scan the DynamoDB table for embeddings
            results = self.dynamodb.scan(
                TableName='Titan_EmbedderRetriever_Vector_DB'
            )

            items = results.get('Items', [])
            retrieved_items = []
            
            # Process each item and calculate similarity
            for item in items:
                embedding = [float(val['N']) for val in item['embedding']['L']]
                similarity = self.calculate_similarity(query_embedding, embedding)
                
                retrieved_items.append({
                    "text": item['text']['S'],
                    "embedding": embedding,
                    "similarity": similarity
                })

            # Sort by similarity and return top_k results
            retrieved_items.sort(key=lambda x: x['similarity'], reverse=True)
            return retrieved_items[:top_k]

        except ClientError as e:
            error_message = e.response['Error']['Message']
            self.logger.error("Error retrieving embeddings from database: %s", error_message)
            raise RetrieveError(f"Database error: {error_message}")

        except Exception as e:
            self.logger.error("Error retrieving embeddings: %s", str(e))
            raise RetrieveError(f"Error retrieving embeddings: {str(e)}")

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
            cls._instance = cls(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                aws_region=aws_region
            )
        return cls._instance

def main():
    """Entrypoint for the TitanRetriever example."""
    try:
        # Create retriever instance
        retriever = TitanRetriever()

        # Example query embedding (replace with actual embedding)
        query_embedding = [0.1, 0.2, 0.3] * 100  # Example 300-dimensional embedding

        # Retrieve similar embeddings
        results = retriever.retrieve_embedding(query_embedding, top_k=3)
        
        print("\nRetrieved similar embeddings:")
        for idx, result in enumerate(results, 1):
            print(f"\n{idx}. Text: {result['text']}")
            print(f"   Similarity score: {result['similarity']:.4f}")

    except RetrieveError as err:
        logger.error(err.message)
        print(f"\nError: {err.message}")

    else:
        print("\nFinished retrieving similar embeddings.")

if __name__ == "__main__":
    main()