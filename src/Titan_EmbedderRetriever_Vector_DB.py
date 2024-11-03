import boto3
from dotenv import load_dotenv
import os
import time  # Import time for sleep functionality

# Load environment variables from the .secrets file
load_dotenv('.secrets')
aws_region = os.getenv("AWS_DEFAULT_REGION")
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_session_token = os.getenv("AWS_SESSION_TOKEN")

def create_dynamodb_table():
    # Initialiser un client DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=aws_region,
                               aws_access_key_id=aws_access_key,
                               aws_secret_access_key=aws_secret_key,
                               aws_session_token=aws_session_token)

    # Définir le nom de la table et les attributs
    table_name = 'Titan_EmbedderRetriever_Vector_DB'
    partition_key = 'embedding_id'  # Clé de partition
    sort_key = 'timestamp'  # Clé de tri (facultatif)

    # Créer la table
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': partition_key,
                    'KeyType': 'HASH'  # Clé de partition
                },
                {
                    'AttributeName': sort_key,
                    'KeyType': 'RANGE'  # Clé de tri
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': partition_key,
                    'AttributeType': 'S'  # Type de l'attribut : String
                },
                {
                    'AttributeName': sort_key,
                    'AttributeType': 'S'  # Type de l'attribut : String
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Table créée avec succès. État de la table : ", table.table_status)
    except Exception as e:
        print("Erreur lors de la création de la table : ", e)

def wait_for_table_creation(dynamodb, table_name):
    table = dynamodb.Table(table_name)
    while True:
        table.reload()  # Refreshes the table object to get the latest state
        if table.table_status == 'ACTIVE':
            print("La table est maintenant active.")
            break
        elif table.table_status == 'CREATING':
            print("La table est toujours en cours de création...")
        else:
            print("État de la table : ", table.table_status)
            break
        time.sleep(5)  # Wait for 5 seconds before checking again

def insert_item(dynamodb, table_name, embedding_id, timestamp):
    table = dynamodb.Table(table_name)
    item = {
        'embedding_id': embedding_id,
        'timestamp': timestamp,
        # Add other attributes here as needed
    }
    
    try:
        table.put_item(Item=item)
        print(f"Item inséré avec succès : {item}")
    except Exception as e:
        print("Erreur lors de l'insertion de l'élément : ", e)

if __name__ == "__main__":
    create_dynamodb_table()
    # After creating the table, wait for it to become active
    dynamodb = boto3.resource('dynamodb', region_name=aws_region,
                               aws_access_key_id=aws_access_key,
                               aws_secret_access_key=aws_secret_key,
                               aws_session_token=aws_session_token)
    wait_for_table_creation(dynamodb, 'Titan_EmbedderRetriever_Vector_DB')
    insert_item(dynamodb, 'Titan_EmbedderRetriever_Vector_DB', 'embedding_1', '2024-11-03T12:00:00Z') 