

import os
import boto3
import json
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from retriever import Retriever

class Transformer:
    """
    A transformer class for interacting with AWS Bedrock Runtime service with context retrieval.
    """
    
    def __init__(self, 
                 env_file: str = '.secrets',
                 model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
                 max_tokens: int = 512,
                 temperature: float = 0.5):
        """
        Initialize the BedrockTransformer with AWS credentials and model parameters.
        
        Args:
            env_file (str): Path to the environment file containing AWS credentials
            model_id (str): The Bedrock model ID to use
            max_tokens (int): Maximum number of tokens in the response
            temperature (float): Temperature parameter for response generation
        """
        self.load_credentials(env_file)
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = self._initialize_client()
        self.retriever = Retriever()  # Initialize the Retriever
        
    def load_credentials(self, env_file: str) -> None:
        """Load AWS credentials from environment file."""
        load_dotenv(env_file)
        self.aws_region = os.getenv("AWS_DEFAULT_REGION")
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_session_token = os.getenv("AWS_SESSION_TOKEN")
        
    def _initialize_client(self) -> boto3.client:
        """Initialize and return the Bedrock Runtime client."""
        return boto3.client(
            'bedrock-runtime',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            aws_session_token=self.aws_session_token,
            region_name=self.aws_region
        )
    
    def _create_request_payload(self, prompt: str, context: str) -> Dict[str, Any]:
        """
        Create the request payload for the model with context.
        
        Args:
            prompt (str): The user prompt
            context (str): The retrieved context
            
        Returns:
            Dict[str, Any]: The formatted request payload
        """
        # Combine context and prompt
        full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
        
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": full_prompt}],
                }
            ],
        }
    
    def transform(self, prompt: str) -> Optional[str]:
        """
        Transform the input prompt using the Bedrock model with retrieved context.
        
        Args:
            prompt (str): The input prompt to transform
            
        Returns:
            Optional[str]: The transformed text or None if there's an error
        """
        try:
            # Get context from the Retriever
            context = self.retriever.get_context(query='')
            
            # Create request with combined context and prompt
            request = json.dumps(self._create_request_payload(prompt, context))
            
            # Invoke the model
            response = self.client.invoke_model(modelId=self.model_id, body=request)
            model_response = json.loads(response["body"].read())
            return model_response["content"][0]["text"]
            
        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{self.model_id}'. Reason: {e}")
            return None

def main():
    # Example usage
    transformer = Transformer()
    response = transformer.transform("What is T.Swifts bday")
    if response:
        print(response)

if __name__ == "__main__":
    main()

