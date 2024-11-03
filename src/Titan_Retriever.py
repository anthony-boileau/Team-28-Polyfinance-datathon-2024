import os
import json
import logging
import boto3
import numpy as np
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv('.secrets')

class RetrieveError(Exception):
    """Custom exception for errors during the retrieval process."""
    def __init__(self, message):
        self.message = message

class TitanRetriever:
    """Retriever class for handling embedding queries."""
    logger = logging.getLogger(__name__)

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_session_token, aws_region):
        """Initialize the TitanRetriever with AWS credentials."""
        self.dynamodb = boto3.client(
            service_name='dynamodb',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=aws_region
        )
        self.logger.info("TitanRetriever initialized.")

    def calculate_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def retrieve_embedding(self, query_embedding, top_k=5):
        """Retrieve the top K similar embeddings from the Titan_EmbedderRetriever_Vector_DB."""
        self.logger.info("Retrieving top %d embeddings similar to the query.", top_k)

        try:
            # Instead of 'self.bedrock.query', we use the DynamoDB client to scan or query
            results = self.dynamodb.scan(
                TableName='Titan_EmbedderRetriever_Vector_DB',
                Limit=top_k
            )

            items = results.get('Items', [])
            retrieved_items = []
            for item in items:
                embedding = item['embedding']['L']  # Assuming embedding is stored as a list
                retrieved_items.append({
                    "text": item['text']['S'],  # Assuming text is stored as a string
                    "embedding": [float(val['N']) for val in embedding]  # Convert from DynamoDB format
                })

            # Optionally implement your similarity logic here to filter and return the top_k results
            # For example: Sort retrieved_items based on similarity (not implemented here)
            return retrieved_items[:top_k]

        except ClientError as e:
            self.logger.error("Error retrieving embeddings from database: %s", e.response['Error']['Message'])
            raise RetrieveError("Database error: " + e.response['Error']['Message'])

        except Exception as e:
            self.logger.error("Error retrieving embeddings: %s", str(e))
            raise RetrieveError("Error retrieving embeddings: " + str(e))

def main():
    """Entrypoint for the TitanRetriever example."""
    logging.basicConfig(level=logging.INFO)

    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    aws_region = os.getenv("AWS_DEFAULT_REGION")

    retriever = TitanRetriever(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        aws_region=aws_region
    )

    query_embedding = [0.1, 0.2, 0.3]  # Replace with an actual embedding vector

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