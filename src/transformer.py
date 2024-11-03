import awscli as aws
import boto3 as b
import json

def lambda_handler(event, context):
    # Assume the input is a JSON object
    input_data = event['data']
    
    # Transform the data (e.g., convert to uppercase)
    transformed_data = input_data.upper()
    
    return {
        'statusCode': 200,
        'body': json.dumps({'transformed_data': transformed_data})
    }
