import requests
import json
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_all_ciks(output_file: str = './datadumps/cik_from_sec.json') -> Dict[str, str]:
    """
    Fetch all ticker-CIK mappings and save to JSON file.
    
    Args:
        output_file: Name of output JSON file
        
    Returns:
        Dictionary mapping tickers to CIKs
    """
    try:
        headers = {
            "User-Agent": "Your Name your@email.com",
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov"
        }
        
        response = requests.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch CIK data: HTTP {response.status_code}")
            return {}
            
        # Convert raw data to ticker->CIK mapping
        raw_data = response.json()
        cik_map = {
            company["ticker"]: str(company["cik_str"]).zfill(10)
            for company in raw_data.values()
        }
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(cik_map, f, indent=2, sort_keys=True)
            
        logger.info(f"Saved {len(cik_map)} CIK mappings to {output_file}")
        return cik_map
        
    except Exception as e:
        logger.error(f"Error fetching CIK data: {str(e)}")
        return {}

if __name__ == "__main__":
    fetch_all_ciks()