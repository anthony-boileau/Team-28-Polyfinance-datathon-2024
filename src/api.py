import aiohttp
import asyncio
from sec_functions.get_data_sec_edgar import SECEdgarCollector as edgar
from sec_functions.get_annual_report_form10k_sec import SEC10KParser as sec10k
from datetime import datetime
from singleton_decorator import singleton
import time
import statistics
from collections import defaultdict

@singleton
class API:
    def __init__(self):
        self.collector = edgar()
        self.parser = sec10k()
    
    async def generate_annual_reports(self, ticker, fromYear, toYear=None):
        # Trim and convert ticker to uppercase
        ticker = ticker.strip().upper()
        
        # Set default toYear to current year if not provided
        if toYear is None:
            toYear = datetime.now().year
            
        try:
            # Then call methods on those instances
            step1 = await self.collector.fetch_all(ticker)
            step2 = await self.parser.fetch_and_parse_all_10k_in_range(ticker, fromYear, toYear)
            return step1, step2
        except Exception as e:
            print(f"Error processing request: {str(e)}")
            return None
    
    async def cleanup(self):
        """Cleanup resources"""
        if hasattr(self.collector, 'close'):
            await self.collector.close()
        if hasattr(self.parser, 'close'):
            await self.parser.close()

    async def get_annual_report_content_streamed():
        """
        return the annual report in form of embeddings and metadata
        """

    

async def run_tests():
    companies = ['GOOGL', 'MSFT', 'AAPL', 'AMZN', 'TSLA', 'NFLX', 'FB', 'NVDA', 'DIS']
    times_per_company = defaultdict(list)
    total_time = 0
    all_times = []  # List to store all execution times for population calculations
    
    for company in companies:
        for run in range(3):
            try:
                start_time = time.perf_counter()
                api = API()
                result = await api.generate_annual_reports(company, 2023,2023)
                execution_time = time.perf_counter() - start_time
                times_per_company[company].append(execution_time)
                total_time += execution_time
                all_times.append(execution_time)  # Add each time to all_times list
                print(f"Run {run + 1} for {company}: {execution_time:.3f} seconds")
            finally:
                await api.cleanup()

    # Print statistics per company
    for company in companies:
        company_times = times_per_company[company]
        avg_time = statistics.mean(company_times)
        std_dev = statistics.stdev(company_times)
        print(f"\n{company} Statistics:")
        print(f"Average: {avg_time:.3f} seconds")
        print(f"Std Dev: {std_dev:.3f} seconds")

    overall_average = total_time / (len(companies) * 3)  # 3 runs per company
    overall_std = statistics.pstdev(all_times)  # Calculate population standard deviation
    
    print(f"\nOverall average across all runs: {overall_average:.3f} seconds")
    print(f"Overall population std dev: {overall_std:.3f} seconds")
    
    return True
    
if __name__ == "__main__":
    asyncio.run(run_tests())