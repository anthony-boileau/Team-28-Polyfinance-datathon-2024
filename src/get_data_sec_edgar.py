import aiohttp
import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import logging
from functools import wraps



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def rate_limit():
    """Decorator to add rate limiting to async functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await asyncio.sleep(0.111)  # 111ms delay
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class SECEdgarCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Hackathon polyfinancedatathon2.jp0rh@passmail.net',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        }
    
    def get_cik(self, ticker: str) -> Optional[str]:
        """Get CIK from local JSON file."""
        try:
            ticker = ticker.upper().replace(".", "-")
            with open('./datadumps/cik_from_sec.json', 'r') as f:
                cik_data = json.load(f)
            return cik_data.get(ticker)
                
        except Exception as e:
            logger.error(f"Error reading CIK for {ticker}: {str(e)}")
            return None

    @rate_limit()
    async def fetch_submissions(self, ticker: str, cik: str, timestamp: str) -> bool:
        """Fetch submission data for 10-K forms and include primary document links."""
        try:
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch submission data. Status: {response.status}")
                        return False
                    
                    data = await response.json()
                    cik_padded = str(data.get('cik', '')).zfill(10)
                    data['primaryDocumentLinks'] = []
                    
                    if 'filings' in data:
                        recent = data['filings'].get('recent', {})
                        files = data['filings'].get('files', [])
                        
                        if recent:
                            form_indices = [i for i, form in enumerate(recent.get('form', [])) 
                                            if form == '10-K']
                            
                            for key in recent.keys():
                                if isinstance(recent[key], list):
                                    recent[key] = [recent[key][i] for i in form_indices]
                            
                            for acc_num, primary_doc in zip(recent.get('accessionNumber', []), 
                                                            recent.get('primaryDocument', [])):
                                acc_num = acc_num.replace('-', '')
                                link = f"https://www.sec.gov/Archives/edgar/data/{cik_padded}/{acc_num}/{primary_doc}"
                                data['primaryDocumentLinks'].append(link)
                        
                        filtered_files = []
                        for file_info in files:
                            if isinstance(file_info, dict) and file_info.get('form') == '10-K':
                                acc_num = file_info.get('accessionNumber', '').replace('-', '')
                                primary_doc = file_info.get('primaryDocument', '')
                                if acc_num and primary_doc:
                                    link = f"https://www.sec.gov/Archives/edgar/data/{cik_padded}/{acc_num}/{primary_doc}"
                                    data['primaryDocumentLinks'].append(link)
                                    filtered_files.append(file_info)
                        
                        data['filings']['files'] = filtered_files
                    
                    return await self.dumper(ticker, "submissions", data, timestamp)
                
        except Exception as e:
            logger.error(f"Error in fetch_submissions: {str(e)}")
            return False

    @rate_limit()
    async def fetch_company_facts(self, ticker: str, cik: str, timestamp: str) -> bool:
        """Fetch company facts data and filter for 10-K entries only."""
        try:
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        return False
                        
                    data = await response.json()
                    facts = data.get("facts", {})

                    for taxonomy in facts:
                        for concept in facts[taxonomy]:
                            if "units" in facts[taxonomy][concept]:
                                for unit_type, entries in facts[taxonomy][concept]["units"].items():
                                    facts[taxonomy][concept]["units"][unit_type] = [
                                        entry for entry in entries 
                                        if entry.get("form") == "10-K"
                                    ]
                    
                    return await self.dumper(ticker, "company_facts", data, timestamp)
                    
        except Exception as e:
            logger.error(f"Error in fetch_company_facts: {str(e)}")
            return False

    @rate_limit()
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
            ("submission", self.fetch_submissions(ticker, cik, ts)),
            ("company_facts", self.fetch_company_facts(ticker, cik, ts)),
        ]

        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        return [(data_type, result if not isinstance(result, Exception) else False) 
                for (data_type, _), result in zip(tasks, results)]

async def main():
    collector = SECEdgarCollector()
    await collector.fetch_all('AAPL')

if __name__ == '__main__':
    asyncio.run(main())