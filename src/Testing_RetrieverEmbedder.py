import os
import json
import random
from Titan_Embedder import TitanEmbedder
from Titan_Retriever import TitanRetriever

def test_embedder_and_retriever(embedder, retriever, input_texts, top_k=3):
    # Step 1: Generate embeddings and store them
    embeddings = {}  # Dictionary to store text and their corresponding embeddings
    for text in input_texts:
        try:
            response = embedder.generate_embeddings(text)
            embedding = response['embedding']
            embedder.insert_embedding_to_db(embedding, text)
            embeddings[text] = embedding  # Store the embedding for later verification
            print(f"Inserted embedding for: '{text}'")
        except Exception as e:
            print(f"Error generating/storing embedding for '{text}': {e}")

    # Step 2: Randomly select a text to query
    query_text = random.choice(input_texts)
    print(f"\nQuerying for similar embeddings to: '{query_text}'")

    # Generate embedding for the query text
    try:
        query_response = embedder.generate_embeddings(query_text)
        query_embedding = query_response['embedding']
        
        # Step 3: Retrieve similar embeddings using the retriever
        retrieved_results = retriever.retrieve_embedding(query_embedding, top_k)
        
        print("Retrieved similar embeddings:")
        retrieved_texts = [result['text'] for result in retrieved_results]
        
        # Check if the query text is among the retrieved results
        if query_text in retrieved_texts:
            print(f"Success: The query text '{query_text}' was found in the retrieved results.")
        else:
            print(f"Failure: The query text '{query_text}' was not found in the retrieved results.")

        # Verify that the retrieved embeddings correspond to the stored embeddings
        for result in retrieved_results:
            retrieved_text = result['text']
            if retrieved_text in embeddings:
                stored_embedding = embeddings[retrieved_text]
                retrieved_embedding = result['embedding']
                
                # Check if the stored embedding and retrieved embedding are similar (or the same)
                if retrieved_embedding == stored_embedding:
                    print(f"Success: Retrieved embedding for '{retrieved_text}' matches the stored embedding.")
                else:
                    print(f"Warning: Retrieved embedding for '{retrieved_text}' does NOT match the stored embedding.")
            else:
                print(f"Warning: Retrieved text '{retrieved_text}' was not found in the stored embeddings.")

        # Optionally, print out the retrieved texts and check embeddings
        for result in retrieved_results:
            print(f"Text: {result['text']}, Embedding: {result['embedding']}")

    except Exception as e:
        print(f"Error during retrieval: {e}")

# Example usage
if __name__ == "__main__":
    # Set up AWS credentials and parameters
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    aws_region = os.getenv("AWS_DEFAULT_REGION")

    # Define the model ID
    model_id = "amazon.titan-embed-text-v1"  # Add your model ID here

    # Initialize embedder and retriever
    embedder = TitanEmbedder(
        model_id=model_id,  # Pass the model_id here
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        aws_region=aws_region
    )
    
    retriever = TitanRetriever(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        aws_region=aws_region
    )

    # Define some sample input texts
    input_texts = [
        "What services do you offer?",
        "Tell me about your pricing plans.",
        "How can I contact customer support?",
        "What is your return policy?",
        "Do you have any special offers?"
    ]

    # Run the test
    test_embedder_and_retriever(embedder, retriever, input_texts)