from dbagent import DBagent

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
    dba = DBagent()
    
    print("\nStarting performance tests across all companies...")
    print("=" * 50)
    
    for company in companies:
        try:
            # Record starting metrics
            start_time = time.perf_counter()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            print(f"\nProcessing {company}...")
            # Run the embedding process
            success = await dba.embed_company_over_daterange(company,2024)
            
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
    e = DBagent()
    collection = e.get_collection(name="TSLA")
    result = collection.query(
        query_texts=["what are the risk factors"],
        n_results= 2,
        where={
            "year":{
                "$in": [2024]
                }
        },
        include=["documents","metadatas", "distances"]
    )
    print(type(result))
    print(result)

    