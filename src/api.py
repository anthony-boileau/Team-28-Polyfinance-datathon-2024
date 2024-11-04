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

def annual_report_to_collection(self, ticker: str, year: int) -> Dict[str, Any]:
        """
        Convert an annual report from JSON format to a collection of documents with metadata.
        
        Args:
            ticker (str): The stock ticker symbol
            year (int): The year of the annual report
            
        Returns:
            Dict containing:
                - documents: List of content strings
                - metadatas: List of metadata dicts
                - ids: List of unique identifiers
                
        Raises:
            FileNotFoundError: If the JSON file doesn't exist
            json.JSONDecodeError: If the JSON file is invalid
        """
        # Construct file path
        file_path = Path(f"./json/datadumps/{ticker}_{year}_10k.json")
        
        try:
            # Read and parse JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            metadatas = []
            ids = []
            
            # Process each item and its contents
            for item_index, item_data in enumerate(data.get('items', [])):
                item_name = item_data.get('item', '')
                contents = item_data.get('contents', [])
                
                # Process each content block within the item
                for content_index, content in enumerate(contents):
                    if content and isinstance(content, str):
                        # Add the content to documents
                        documents.append(content)
                        
                        # Create metadata for this content
                        metadata = {
                            'item': item_name,
                            'ticker': ticker,
                            'year': year,
                            'item_index': item_index,
                            'content_index': content_index
                        }
                        metadatas.append(metadata)
                        
                        # Create unique ID
                        unique_id = f"{ticker}_{year}_{item_name}_{item_index}_{content_index}"
                        unique_id = unique_id.replace(' ', '_').replace('.', '')
                        ids.append(unique_id)
            
            collection = {
                'documents': documents,
                'metadatas': metadatas,
                'ids': ids
            }
            
            return collection
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Annual report file not found for {ticker} {year}: {e}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error parsing JSON for {ticker} {year}: {e.msg}", e.doc, e.pos)
        except Exception as e:
            raise Exception(f"Unexpected error processing annual report for {ticker} {year}: {str(e)}")


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