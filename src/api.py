import aiohttp
import asyncio
from sec_functions.get_data_sec_edgar import SECEdgarCollector as edgar
from sec_functions.get_annual_report_form10k_sec import SEC10KParser as sec10k
from datetime import datetime
from singleton_decorator import singleton
import time
import statistics
from collections import defaultdict
import json

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
            # Call methods on instances
            step1 = await self.collector.fetch_all(ticker)
            step2 = await self.parser.fetch_and_parse_all_10k_in_range(ticker, fromYear, toYear)
            return True
        except Exception as e:
            print(f"Error processing request: {str(e)}")
            return False  # Changed from None to False for consistency
    
    async def cleanup(self):
        """Cleanup resources"""
        if hasattr(self.collector, 'close'):
            await self.collector.close()
        if hasattr(self.parser, 'close'):
            await self.parser.close()

    def annual_report_to_collection(self, ticker, year):
        """
        Convert an annual report from JSON format to a collection of documents with metadata
        and save it to a collection JSON file.
        
        Args:
            ticker (str): The stock ticker symbol
            year (int): The year of the annual report
                
        Returns:
            bool: True if successful, False if any errors occurred
        """
        input_file_path = f"./json/datadumps/{ticker}-{year}-10k.json"
        output_file_path = f"./json/datadumps/{ticker}-{year}-10k-collection.json"
        
        try:
            with open(input_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            metadatas = []
            ids = []
            
            for item_index, item_data in enumerate(data.get('items', [])):
                item_name = item_data.get('item', '')
                contents = item_data.get('contents', [])
                
                for content_index, content in enumerate(contents):
                    if content and isinstance(content, str):
                        documents.append(content)
                        
                        metadata = {
                            'item': item_name,
                            'ticker': ticker,
                            'year': year,
                        }
                        metadatas.append(metadata)
                        
                        unique_id = f"{ticker}_{year}_{item_name}_{item_index}_{content_index}"
                        unique_id = unique_id.replace(' ', '_').replace('.', '')
                        ids.append(unique_id)
            
            collection = {
                'documents': documents,
                'metadatas': metadatas,
                'ids': ids
            }
            
            # Write the collection to a new JSON file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(collection, f, ensure_ascii=False, indent=2)
                
            print(f"Collection successfully written to {output_file_path}")
            return True
                
        except FileNotFoundError as e:
            print(f"Annual report file not found for {ticker} {year}: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for {ticker} {year}: {e.msg}")
            return False
        except Exception as e:
            print(f"Unexpected error processing annual report for {ticker} {year}: {str(e)}")
            return False

    async def batch_get_collections(self, ticker, fromYear, toYear=None):
        """
        Generate and process annual reports for a given ticker across a range of years.
        
        Args:
            ticker (str): The stock ticker symbol
            fromYear (int): Starting year
            toYear (int, optional): Ending year. Defaults to current year if not provided.
        
        Returns:
            bool: True if successful, False if any errors occurred
        """
        # Set default toYear to current year if not provided
        if toYear is None:
            toYear = datetime.now().year
            
        try:
            # First generate all annual reports for the year range
            generated = await self.generate_annual_reports(ticker, fromYear, toYear)
            if not generated:
                print(f"Failed to generate annual reports for {ticker} from {fromYear} to {toYear}")
                return False
                
            # Process each year's report into a collection
            success = True
            for year in range(fromYear, toYear + 1):
                try:
                    result = self.annual_report_to_collection(ticker, year)
                    if not result:
                        print(f"Failed to create collection for {ticker} {year}")
                        success = False
                except Exception as e:
                    print(f"Error processing collection for {ticker} {year}: {str(e)}")
                    success = False
                    
            return success
                    
        except Exception as e:
            print(f"Error in batch processing for {ticker}: {str(e)}")
            return False

async def run_batch_collection_test():
    """Test the batch collection processing"""
    api = API()
    try:
        # Test with a single company for 2 years
        success = await api.batch_get_collections('TSLA', 2020, 2021)  # Added end year
        if success:
            print("Batch processing completed successfully")
        else:
            print("Batch processing encountered some errors")
    finally:
        await api.cleanup()

async def run_generate_tests():
    """Run performance tests on multiple companies"""
    companies = ['GOOGL', 'MSFT', 'AAPL', 'AMZN', 'TSLA', 'NFLX', 'FB', 'NVDA', 'DIS']
    times_per_company = defaultdict(list)
    total_time = 0
    all_times = []
    api = API()  # Create single API instance outside the loop
    
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
            if len(company_times) > 1:  # Need at least 2 values for std dev
                avg_time = statistics.mean(company_times)
                std_dev = statistics.stdev(company_times)
                print(f"\n{company} Statistics:")
                print(f"Average: {avg_time:.3f} seconds")
                print(f"Std Dev: {std_dev:.3f} seconds")

        if all_times:  # Only calculate if we have data
            overall_average = total_time / len(all_times)
            overall_std = statistics.pstdev(all_times)
            print(f"\nOverall average across all runs: {overall_average:.3f} seconds")
            print(f"Overall population std dev: {overall_std:.3f} seconds")
            
        return True
    finally:
        await api.cleanup()

def collection_test():
    """Test the collection conversion for a single company"""
    api = API()
    return api.annual_report_to_collection('TSLA', 2023)

if __name__ == "__main__":
    asyncio.run(run_batch_collection_test())