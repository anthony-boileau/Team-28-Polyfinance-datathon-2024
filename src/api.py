import aiohttp
import asyncio
from sec_functions.get_data_sec_edgar import SECEdgarCollector as edgar
from sec_functions.get_annual_report_form10k_sec import SEC10KParser as sec10k
from datetime import datetime
from singleton_decorator import singleton

@singleton
class API:
    def __init__(self):
        self.collector = edgar()
        self.parser = sec10k()
    
    async def get_annual_report(self, ticker, fromYear, toYear=None):
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

async def main():
    try:
        api = API()  # Will always return the same instance
        result = await api.get_annual_report('RACE', 2022)
        return result
    finally:
        await api.cleanup()

if __name__ == "__main__":
    asyncio.run(main())