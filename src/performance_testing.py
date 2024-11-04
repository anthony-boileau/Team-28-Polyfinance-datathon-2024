from dbagent import DBagent
from transformer import Transformer
import time
import numpy as np
from typing import List, Tuple
from api import API
from collections import defaultdict
import statistics
import psutil

async def measure_embedding_performance_metrics():
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
            success = await dba.embed_company_over_daterange(company, 2024)
            
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

async def execute_embedding_performance_suite():
    """Main function to run embedding performance test suite."""
    try:
        start_time = time.perf_counter()
        stats = await measure_embedding_performance_metrics()
        total_time = time.perf_counter() - start_time
        
        print("\nTotal test execution time:", f"{total_time:.2f} seconds")
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
    finally:
        print("\nTest execution completed")

def benchmark_transformer_performance(num_runs: int = 10) -> Tuple[float, float]:
    """
    Time multiple transformer runs and return mean and standard deviation.
    
    Args:
        num_runs: Number of transformer runs to time
    
    Returns:
        Tuple of (mean_time, std_dev)
    """
    # Initialize objects
    dba = DBagent()
    t = Transformer()
    
    # Different prompts to test variety of inputs
    prompts = [
        "what are the risk factors",
        "describe the competitive landscape",
        "what are the main revenue streams",
        "explain the business model",
        "list major acquisitions",
        "discuss regulatory challenges",
        "outline growth strategy",
        "analyze market position",
        "detail operational risks",
        "evaluate financial performance"
    ]
    
    # Store timing results
    times: List[float] = []
    
    for i, prompt in enumerate(prompts[:num_runs]):
        # Time the entire process
        start_time = time.time()
        
        # Get context and transform
        context = dba.get_context(
            prompt=prompt,
            fromYear=2024,
            ticker="TSLA"
        )
        t.transform(context=context, prompt=prompt)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        times.append(elapsed_time)
        
        print(f"Run {i+1}/{num_runs} completed in {elapsed_time:.2f} seconds")
    
    # Calculate statistics
    mean_time = np.mean(times)
    std_dev = np.std(times)
    
    # Print detailed results
    print("\nDetailed Results:")
    print(f"Mean execution time: {mean_time:.2f} seconds")
    print(f"Standard deviation: {std_dev:.2f} seconds")
    print(f"Min time: {min(times):.2f} seconds")
    print(f"Max time: {max(times):.2f} seconds")
    
    return mean_time, std_dev

async def test_batch_collection_processing():
    """Test the batch collection processing for a single company"""
    api = API()
    try:
        # Test with a single company for 2 years
        success = await api.batch_get_collections('TSLA', 2020, 2021)
        if success:
            print("Batch processing completed successfully")
        else:
            print("Batch processing encountered some errors")
    finally:
        await api.cleanup()

async def benchmark_report_generation():
    """Run performance tests for report generation across multiple companies"""
    companies = ['GOOGL', 'MSFT', 'AAPL', 'AMZN', 'TSLA', 'NFLX', 'FB', 'NVDA', 'DIS']
    times_per_company = defaultdict(list)
    total_time = 0
    all_times = []
    api = API()
    
    try:
        for company in companies:
            for run in range(3):
                try:
                    start_time = time.perf_counter()
                    result = await api.generate_annual_reports(company, 2023, 2023)
                    execution_time = time.perf_counter() - start_time
                    times_per_company[company].append(execution_time)
                    total_time += execution_time
                    all_times.append(execution_time)
                    print(f"Run {run + 1} for {company}: {execution_time:.3f} seconds")
                except Exception as e:
                    print(f"Error in run {run + 1} for {company}: {str(e)}")

        # Calculate statistics
        for company in companies:
            company_times = times_per_company[company]
            if len(company_times) > 1:
                avg_time = statistics.mean(company_times)
                std_dev = statistics.stdev(company_times)
                print(f"\n{company} Statistics:")
                print(f"Average: {avg_time:.3f} seconds")
                print(f"Std Dev: {std_dev:.3f} seconds")

        if all_times:
            overall_average = total_time / len(all_times)
            overall_std = statistics.pstdev(all_times)
            print(f"\nOverall average across all runs: {overall_average:.3f} seconds")
            print(f"Overall population std dev: {overall_std:.3f} seconds")
            
        return True
    finally:
        await api.cleanup()

def test_single_report_collection():
    """Test the collection conversion for a single company's annual report"""
    api = API()
    return api.annual_report_to_collection('TSLA', 2023)

if __name__ == "__main__":
    mean, std = benchmark_transformer_performance()