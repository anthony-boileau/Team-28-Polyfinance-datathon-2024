import os
import json
import logging
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from the .secrets file
load_dotenv('.secrets')

class EmbedError(Exception):
    "Custom exception for errors returned by Amazon Titan Multimodal Embeddings G1"

    def __init__(self, message):
        self.message = message

class TitanEmbedder:
    # Class-level logger
    logger = logging.getLogger(__name__)

    def __init__(self, model_id, aws_access_key_id, aws_secret_access_key, aws_session_token, aws_region):
        """
        Initialize the TitanEmbedder with AWS credentials and model ID.
        Args:
            model_id (str): The model ID to use.
            aws_access_key_id (str): AWS Access Key ID.
            aws_secret_access_key (str): AWS Secret Access Key.
            aws_session_token (str): AWS Session Token.
            aws_region (str): AWS Default Region.
        """
        self.model_id = model_id
        self.bedrock = boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=aws_region
        )
        self.logger.info("TitanEmbedder initialized with model ID: %s", model_id)

    def generate_embeddings(self, input_text):
        """
        Generate a vector of embeddings for a text input using Amazon Titan Multimodal Embeddings G1 on demand.
        Args:
            input_text (str): The input text to generate embeddings for.
        Returns:
            response (JSON): The embeddings that the model generated, token information, and the
            reason the model stopped generating embeddings.
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

    def insert_embedding_to_db(self, embedding, input_text):
        """
        Insert the generated embeddings into a vector database.
        This is a mock function; implement your actual database insertion logic here.
        """
        self.logger.info("Inserting embedding into the database for the input text.")
        # Example: Adjust according to your vector database's SDK/API
        # db_client.insert({"text": input_text, "embedding": embedding})  # Hypothetical call
        print(f"Inserted embedding for text: {input_text} into the database.")  # Mock print


def main():
    """
    Entrypoint for Amazon Titan Multimodal Embeddings G1 example.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Initialize AWS credentials and parameters
    model_id = "amazon.titan-embed-text-v1"
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    aws_region = os.getenv("AWS_DEFAULT_REGION")

    # Create an instance of TitanEmbedder
    embedder = TitanEmbedder(
        model_id=model_id,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        aws_region=aws_region
    )

    input_text = "What are the different services that you offer?"

    try:
        response = embedder.generate_embeddings(input_text)
        embedding = response['embedding']
        
        print(f"Generated text embeddings: {embedding}")
        print(f"Input text token count:  {response['inputTextTokenCount']}")

        # Insert the embedding into the database
        embedder.insert_embedding_to_db(embedding, input_text)

    except EmbedError as err:
        TitanEmbedder.logger.error(err.message)
        print(err.message)

    else:
        print(f"Finished generating text embeddings with Amazon Titan Multimodal Embeddings G1 model {model_id}.")


if __name__ == "__main__":
    main()