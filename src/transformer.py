"""
import os
import boto3
import json
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from the .secrets file
load_dotenv('.secrets')
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

def main():

    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client(
        'bedrock-runtime',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=AWS_DEFAULT_REGION
    )

    # Set the model ID to Claude 3 Sonnet v1.
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

    # Define the prompt for the model.
    prompt = "What is your purpose"

    # Format the request payload using the model's native structure.
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["content"][0]["text"]
    print(response_text)

if __name__ == "__main__":
    main()
"""
import os
import boto3
import json
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import retriever

class Agent:
    def __init__(self):
        # Load environment variables from the .secrets file
        load_dotenv('.secrets')

        # Fetch AWS credentials and region from environment variables
        self.aws_default_region = os.getenv("AWS_DEFAULT_REGION")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_session_token = os.getenv("AWS_SESSION_TOKEN")  # Optional

        # Create a Bedrock Runtime client
        self.client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.aws_default_region
        )

        # Set the model ID
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

    def invoke_model(self, prompt):
        # Format the request payload using the model's native structure

        context = retriever.get_context('')
        prompt = context + prompt
        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0.5,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        }

        # Convert the native request to JSON
        request = json.dumps(native_request)

        try:
            # Invoke the model with the request
            response = self.client.invoke_model(modelId=self.model_id, body=request)
        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{self.model_id}'. Reason: {e}")
            return None

        # Decode the response body
        model_response = json.loads(response["body"].read())

        # Extract and return the response text
        return model_response["content"][0]["text"]

def main():
    agent = Agent()  # Create an instance of the Agent class
    prompt = "What is your purpose?"  # Define the prompt
    response = agent.invoke_model(prompt)  # Invoke the model with the prompt
    print("Model Response:", response)  # Print the response

if __name__ == "__main__":
    main()
