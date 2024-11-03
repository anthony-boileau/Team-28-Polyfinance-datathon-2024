import requests
from dotenv import load_dotenv
import os

# Load environment variables from .secrets file
load_dotenv(".secrets")

# Retrieve API key from environment
API_KEY = os.getenv("API_KEY")

def get_cik_from_ticker(ticker):
    """
    Retrieve the CIK for a given ticker symbol from Financial Modeling Prep API.
    """
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={API_KEY}"
    response = requests.get(url)
    
    # Check if the response is successful
    if response.status_code == 200:
        data = response.json()
        if data:
            cik = data[0].get('cik')
            if cik:
                return cik
            else:
                print("CIK not found in response.")
        else:
            print("No data found for ticker.")
    else:
        print(f"Failed to retrieve data: {response.status_code}")
    return None

def get_company_submissions(cik):
    """
    Retrieve company submission data from SEC EDGAR API using the CIK.
    """
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {
        "User-Agent": "Your Name <your-email@example.com>"
    }
    response = requests.get(url, headers=headers)
    
    # Check if the response is successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve SEC data: {response.status_code}")
    return None
