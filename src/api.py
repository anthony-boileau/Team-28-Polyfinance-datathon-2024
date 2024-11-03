import aiohttp
import asyncio
from sec_functions import SECEdgarCollector, SEC10KParser

def api_get(self,ticker,fromYear,toYear):
    step1 = SECEdgarCollector.fetch_all(ticker)
    step2 = SEC10KParse.fetch_and_parse_all_10k_in_range(ticker,fromYear,toYear)
    
