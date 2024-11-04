import boto3
from dotenv import load_dotenv
import os
import time
import chromadb
import asyncio
import json
import psutil
import statistics
from datetime import datetime
from chromadb.config import Settings
from singleton_decorator import singleton
from api import API as api

@singleton
class Embedder:
    def __init__(self):
        """Initialize the Embedder with ChromaDB client."""
        try:
            self._client = chromadb.PersistentClient(
                path="./database",
                settings=Settings(allow_reset=True,
                                anonymized_telemetry=False)
            )
        except Exception as e:
            print(f"Error initializing ChromaDB client: {str(e)}")
            raise

    def __getattr__(self, name):
        """Delegate any unknown attributes/methods to the client."""
        return getattr(self._client, name)


    def tokenize_annual_report(self, filepath, collection):
        """
        Read and process an annual report JSON file and upsert it into the collection.
        
        Args:
            filepath (str): Path to the JSON file containing the annual report
            collection: ChromaDB collection object
        
        Returns:
            bool: True if successful, False if any errors occurred
        """
        try:
            # Read and parse the JSON file
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not all(key in data for key in ['documents', 'metadatas', 'ids']):
                print(f"Invalid JSON format in {filepath}. Missing required keys.")
                return False

            # Validate data lengths match
            if not (len(data['documents']) == len(data['metadatas']) == len(data['ids'])):
                print(f"Mismatched lengths in {filepath} data")
                return False

            # Upsert the data into the collection
            collection.upsert(
                documents=data['documents'],
                metadatas=data['metadatas'],
                ids=data['ids']
            )
            
            print(f"Successfully processed and upserted {filepath}")
            return True

        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return False
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in {filepath}: {str(e)}")
            return False
        except Exception as e:
            print(f"Error processing {filepath}: {str(e)}")
            return False

    async def embed_company_over_daterange(self, ticker, fromYear, toYear=None):
        """
        Embed all annual reports for a company within the specified year range.
        
        Args:
            ticker (str): Company ticker symbol
            fromYear (int): Starting year
            toYear (int, optional): Ending year. Defaults to current year if not provided.
        
        Returns:
            bool: True if successful, False if any errors occurred
        """
        if toYear is None:
            toYear = datetime.now().year

        try:
            # Get or create collection for this company
            collection = self.get_or_create_collection(ticker)
            
            # Generate the collections using the API
            api_instance = api()
            success = await api_instance.batch_get_collections(ticker, fromYear, toYear)
            
            if not success:
                print(f"Failed to generate collections for {ticker}")
                return False

            # Process each year's report
            for year in range(fromYear, toYear + 1):
                filepath = f"./json/datadumps/{ticker}-{year}-10k-collection.json"
                if not self.tokenize_annual_report(filepath, collection):
                    print(f"Failed to process {year} for {ticker}")
                    return False

            print(f"Successfully embedded all reports for {ticker} from {fromYear} to {toYear}")
            return True

        except Exception as e:
            print(f"Error embedding company {ticker}: {str(e)}")
            return False

async def run_performance_tests():
    """
    Run performance tests across all companies and collect metrics.
    Returns summary statistics for execution time and memory usage.
    """
    companies = ['GOOGL', 'MSFT', 'AAPL', 'AMZN', 'TSLA', 'NFLX', 'META', 'NVDA', 'DIS', 'UBER']
    
    # Initialize metrics collections
    execution_times = []
    memory_usages = []
    process = psutil.Process()
    embedder = Embedder()
    
    print("\nStarting performance tests across all companies...")
    print("=" * 50)
    
    for company in companies:
        try:
            # Record starting metrics
            start_time = time.perf_counter()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            print(f"\nProcessing {company}...")
            # Run the embedding process
            success = await embedder.embed_company_over_daterange(company,2024)
            
            # Record ending metrics
            end_time = time.perf_counter()
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Calculate metrics for this run
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            
            # Store metrics
            execution_times.append(execution_time)
            memory_usages.append(memory_usage)
            
            # Print individual results
            print(f"{'Success' if success else 'Failed'} - {company}:")
            print(f"Execution time: {execution_time:.2f} seconds")
            print(f"Memory usage: {memory_usage:.2f} MB")
            
        except Exception as e:
            print(f"Error processing {company}: {str(e)}")
    
    # Calculate summary statistics
    stats = {
        'time': {
            'mean': statistics.mean(execution_times),
            'std': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            'min': min(execution_times),
            'max': max(execution_times)
        },
        'memory': {
            'mean': statistics.mean(memory_usages),
            'std': statistics.stdev(memory_usages) if len(memory_usages) > 1 else 0,
            'min': min(memory_usages),
            'max': max(memory_usages)
        }
    }
    
    # Print summary statistics
    print("\n" + "=" * 50)
    print("Performance Test Summary")
    print("=" * 50)
    print("\nExecution Time Statistics:")
    print(f"Mean: {stats['time']['mean']:.2f} seconds")
    print(f"Std Dev: {stats['time']['std']:.2f} seconds")
    print(f"Range: {stats['time']['min']:.2f} - {stats['time']['max']:.2f} seconds")
    
    print("\nMemory Usage Statistics:")
    print(f"Mean: {stats['memory']['mean']:.2f} MB")
    print(f"Std Dev: {stats['memory']['std']:.2f} MB")
    print(f"Range: {stats['memory']['min']:.2f} - {stats['memory']['max']:.2f} MB")
    
    return stats

async def main():
    """Main function to run performance tests."""
    try:
        start_time = time.perf_counter()
        stats = await run_performance_tests()
        total_time = time.perf_counter() - start_time
        
        print("\nTotal test execution time:", f"{total_time:.2f} seconds")
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
    finally:
        print("\nTest execution completed")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the async main function
    asyncio.run(main())