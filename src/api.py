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



if __name__ == "__main__":
    pass