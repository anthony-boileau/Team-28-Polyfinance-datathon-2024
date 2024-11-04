import boto3
from dotenv import load_dotenv
import os
import time
import chromadb
from botocore.exceptions import ClientError

"""
Run once to create a chroma db instance in your AWS
"""


def main():
    # Load environment variables
    load_dotenv('.secrets')
    
    # AWS credentials
    aws_region = os.getenv("AWS_DEFAULT_REGION")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    
    # Stack configuration
    stack_name = "t28-chroma-db"
    template_url = "https://s3.amazonaws.com/public.trychroma.com/cloudformation/latest/chroma.cf.json"
    
    # Initialize AWS client
    cf_client = boto3.client(
        'cloudformation',
        region_name=aws_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        aws_session_token=aws_session_token
    )

    # Create stack parameters
    parameters = [
        {
            'ParameterKey': 'InstanceType',
            'ParameterValue': 't3.small'
        }
    ]
    
    try:
        # Create the stack
        response = cf_client.create_stack(
            StackName=stack_name,
            TemplateURL=template_url,
            Parameters=parameters,
            Capabilities=['CAPABILITY_IAM']
        )
        print(f"Stack creation initiated. Stack ID: {response['StackId']}")
        
        # Wait for stack creation
        print("Waiting for stack creation to complete...")
        start_time = time.time()
        timeout = 900  # 15 minutes
        
        while time.time() - start_time < timeout:
            try:
                response = cf_client.describe_stacks(StackName=stack_name)
                stack_status = response['Stacks'][0]['StackStatus']
                
                if stack_status == 'CREATE_COMPLETE':
                    print("Stack creation completed successfully!")
                    
                    # Get instance IP
                    outputs = response['Stacks'][0]['Outputs']
                    instance_ip = None
                    for output in outputs:
                        if 'PublicIp' in output['OutputKey']:
                            instance_ip = output['OutputValue']
                            print(f"ChromaDB instance IP: {instance_ip}")
                            break
                    
                    if instance_ip:
                        # Wait for ChromaDB to start
                        print("Waiting for ChromaDB to start...")
                        time.sleep(120)  # Wait 2 minutes
                        
                        # Initialize ChromaDB client
                        try:
                            chroma_client = chromadb.HttpClient(
                                host=instance_ip,
                                port=8000
                            )
                            chroma_client.heartbeat()
                            print("Successfully connected to ChromaDB!")
                            return chroma_client
                        except Exception as e:
                            print(f"Error connecting to ChromaDB: {e}")
                            return None
                            
                elif stack_status in ['CREATE_FAILED', 'ROLLBACK_COMPLETE']:
                    print(f"Stack creation failed with status: {stack_status}")
                    return None
                
                time.sleep(30)  # Wait 30 seconds before checking again
                
            except ClientError as e:
                print(f"Error checking stack status: {e}")
                return None
        
        print("Timeout waiting for stack creation")
        return None
        
    except ClientError as e:
        print(f"Error creating stack: {e}")
        return None

if __name__ == "__main__":
    chroma_client = main()
    print('Done')