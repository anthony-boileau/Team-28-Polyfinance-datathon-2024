import aiohttp
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables from .secrets file
load_dotenv(".secrets")
# Retrieve API key from environment
API_KEY = os.getenv("SEC_API")

async def get_cik_from_ticker(ticker, session):
    """
    Retrieve the CIK for a given ticker symbol from Financial Modeling Prep API.
    """
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={API_KEY}"
    
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            if data:
                cik = data[0].get('cik')
                if cik:
                    return cik
                else:
                    print("CIK not found in response.")
            else:
                print("No data found for ticker.")
        else:
            print(f"Failed to retrieve data: {response.status}")
        return None

async def get_company_submissions(cik, session):
    """
    Retrieve company submission data from SEC EDGAR API using the CIK.
    """
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {
        "User-Agent": "Your Name <your-email@example.com>"
    }
    
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Failed to retrieve SEC data: {response.status}")
            return None

async def get_company_data_from_ticker(ticker):
    """
    Retrieve company data by combining CIK lookup and SEC submission data.
    Returns None if either API call fails.
    """
    async with aiohttp.ClientSession() as session:
        # First get the CIK from the ticker
        cik = await get_cik_from_ticker(ticker, session)
        
        if cik is None:
            print(f"Could not retrieve CIK for ticker {ticker}")
            return None
            
        # Format CIK to 10 digits with leading zeros
        formatted_cik = str(cik).zfill(10)
        
        # Get the company submissions using the CIK
        submissions = await get_company_submissions(formatted_cik, session)
        
        if submissions is None:
            print(f"Could not retrieve submissions for CIK {formatted_cik}")
            return None
            
        return submissions

async def main():
    """
    Main function to demonstrate usage
    """
    ticker = "AAPL"  # Example ticker
    result = await get_company_data_from_ticker(ticker)
    
    if result:
        print(f"Successfully retrieved data for {ticker}")
        # Process the results as needed
        print(result)

if __name__ == '__main__':
    asyncio.run(main())
    
