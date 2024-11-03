import aiohttp
import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SECDataCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Hackathon polyfinancedatathon2.jp0rh@passmail.net',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        }
    
    def get_cik(self, ticker: str) -> Optional[str]:
        """
        Get CIK from local JSON file.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Optional[str]: CIK number or None if not found
        """
        try:
            ticker = ticker.upper().replace(".", "-")
            with open('./datadumps/cik_from_sec.json', 'r') as f:
                cik_data = json.load(f)
            return cik_data.get(ticker)
                
        except Exception as e:
            logger.error(f"Error reading CIK for {ticker}: {str(e)}")
            return None

    async def fetch_submission(self, ticker: str, cik: str, timestamp: str) -> bool:
        """Fetch and dump submission data."""
        try:
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch submission data. Status: {response.status}")
                        return False
                    
                    data = await response.json()
                    return await self.dumper(ticker, "submission", data, timestamp)
                    
        except Exception as e:
            logger.error(f"Error in fetch_submission: {str(e)}")
            return False

    async def fetch_company_facts(self, ticker: str, cik: str, timestamp: str) -> bool:
        """
        Fetch company facts data and filter for 10-K entries only.
        
        Args:
            ticker: Stock ticker symbol
            cik: Company CIK number
            timestamp: Timestamp for file naming
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        return False
                        
                    data = await response.json()
                    facts = data.get("facts", {})

                    flag = False
                    if (flag):
                        data = {k: {concept: {k2:v2 for k2,v2 in v.items() if k2 != "units"} for concept, v in facts.items()} for k, facts in data.get("facts", {}).items()}
                    else:
                        # Filter for 10-K entries only
                        for taxonomy in facts:  # dei and us-gaap
                            for concept in facts[taxonomy]:
                                if "units" in facts[taxonomy][concept]:
                                    for unit_type, entries in facts[taxonomy][concept]["units"].items():
                                        facts[taxonomy][concept]["units"][unit_type] = [
                                            entry for entry in entries 
                                            if entry.get("form") == "10-K"
                                        ]
                        
                    
                    return await self.dumper(ticker, "company_facts", data, timestamp)
                    
        except Exception:
            return False


    async def dumper(self, ticker: str, data_type: str, data: Dict, timestamp: str) -> bool:
        """Generic data dumper."""
        try:
            filename = f"./datadumps/{ticker}_{data_type}.json"
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            
            logger.info(f"Successfully saved {data_type} data for {ticker} to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error in dumper for {ticker} ({data_type}): {str(e)}")
            return False

    async def fetch_all(self, ticker: str, timestamp: Optional[str] = None) -> List[Tuple[str, bool]]:
        """Fetch all available data types for a ticker."""
        cik = self.get_cik(ticker)
        if not cik:
            return []

        ts = timestamp or datetime.now().strftime('%Y%m%d_%H%M%S')

        tasks = [
            ("submission", self.fetch_submission(ticker, cik, ts)),
            ("company_facts", self.fetch_company_facts(ticker, cik, ts)),
        ]

        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        return [(data_type, result if not isinstance(result, Exception) else False) 
                for (data_type, _), result in zip(tasks, results)]

async def main():
    # Initialize collector
    collector = SECDataCollector()
    
    # Example usage
    ticker = "AAPL"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Fetch all data types
    results = await collector.fetch_all(ticker, timestamp)
    

if __name__ == '__main__':
    asyncio.run(main())