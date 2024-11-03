import aiohttp
import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import logging
from functools import wraps
from bs4 import BeautifulSoup

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

class SEC10KParser:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Hackathon polyfinancedatathon2.jp0rh@passmail.net',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive'
        }

    def clean_html(self, soup):
        """
        Clean HTML by:
        1. Only keeping content within <p> and <span> tags
        2. Converting all tags to lowercase
        3. Removing all other tags and attributes
        
        Args:
            soup: BeautifulSoup object
        
        Returns:
            BeautifulSoup object with cleaned HTML containing only p and span tags
        
        Raises:
            ValueError: If input soup is None
            TypeError: If input is not a BeautifulSoup object
        """
        # Input validation
        if soup is None:
            raise ValueError("Input soup cannot be None")
        if not isinstance(soup, BeautifulSoup):
            raise TypeError(f"Expected BeautifulSoup object, got {type(soup)}")

        # Set of allowed tags
        ALLOWED_TAGS = {'p', 'span'}

        try:
            # Find all tags in the document
            all_tags = soup.find_all()
            
            for tag in all_tags:
                try:
                    # Skip if tag is None or has been decomposed
                    if tag is None or not hasattr(tag, 'name'):
                        continue

                    # Convert tag name to lowercase
                    tag.name = tag.name.lower() if tag.name else ''
                    
                    # If tag is not p or span, replace it with its contents
                    if tag.name not in ALLOWED_TAGS:
                        try:
                            tag.unwrap()  # This preserves the content but removes the tag
                        except Exception as e:
                            logger.warning(f"Failed to unwrap tag {tag.name}: {str(e)}")
                        continue
                    
                    # For p and span tags, remove all attributes
                    if hasattr(tag, 'attrs'):
                        tag.attrs = {}

                except Exception as e:
                    logger.warning(f"Failed to process tag: {str(e)}")
                    continue

            # Remove any remaining tags that aren't p or span
            for tag in soup.find_all(lambda x: x.name not in ALLOWED_TAGS and x.name is not None):
                try:
                    tag.decompose()
                except Exception as e:
                    logger.warning(f"Failed to remove non-allowed tag {tag.name}: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to clean HTML: {str(e)}")
            raise

        # Final validation of cleaned soup
        try:
            # Ensure we still have valid HTML
            if not soup.find():
                logger.warning("Cleaning resulted in empty HTML")
        except Exception as e:
            logger.error(f"Failed to validate cleaned HTML: {str(e)}")

        return soup

    @rate_limit()
    async def fetch_single_10k(self, ticker: str, link: str, i: int, total: int) -> Tuple[bool, Optional[str], Optional[str]]:
        """Helper function to fetch a single 10-K document with rate limiting."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(link, headers=self.headers, allow_redirects=True) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch 10-K document {i+1}/{total} for {ticker}.")
                        logger.error(f"Status: {response.status}, URL: {link}")
                        logger.error(f"Response headers: {response.headers}")
                        return False, None, None
                    
                    content = await response.text()
                    parts = link.split('/')
                    acc_num = parts[-2]
                    doc_name = parts[-1]
                    
                    # Parse HTML content
                    try:
                        # First try parsing as XML
                        soup = BeautifulSoup(content, 'xml')
                    except Exception as e:
                        # If XML parsing fails, fall back to HTML parsing
                        logger.warning(f"XML parsing failed for {ticker}, falling back to HTML parser")
                        soup = BeautifulSoup(content, 'html.parser')
                    
                    # Clean the HTML/XML content
                    #soup = self.clean_html(soup)
                    
                    # Save the cleaned content
                    output_path = f"./datadumps/{ticker}_{acc_num}_{doc_name}.xml"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        # Using prettify() for better readability
                        f.write(soup.prettify())
                    
                    logger.info(f"Successfully downloaded and cleaned 10-K {i+1}/{total} for {ticker}")
                    return True, acc_num, doc_name
                    
        except Exception as e:
            logger.error(f"Error processing link {i+1}/{total} for {ticker}: {str(e)}")
            logger.error(f"Failed URL: {link}")
            return False, None, None

    async def fetch_and_parse_all_10k(self, ticker: str) -> bool:
        """Fetch and parse 10-K documents from stored submission data."""
        try:
            # Read submission data
            submission_file = f"./datadumps/{ticker}_submissions.json"

            with open(submission_file, 'r') as f:
                submission_data = json.load(f)

            # Extract and verify links
            links = submission_data.get('primaryDocumentLinks', [])
            if not links:
                logger.error(f"No 10-K links found for {ticker}")
                return False

            # Create tasks for parallel processing
            tasks = []
            for i, link in enumerate(links):
                task = asyncio.create_task(
                    self.fetch_single_10k(ticker, link, i, len(links))
                )
                tasks.append(task)

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            success = all(isinstance(r, tuple) and r[0] for r in results)
            if success:
                logger.info(f"Successfully processed all 10-K documents for {ticker}")
            else:
                logger.warning(f"Some 10-K documents failed to process for {ticker}")
            
            return success

        except Exception as e:
            logger.error(f"Error in fetch_and_parse_10k for {ticker}: {str(e)}")
            return False

async def main():
    parser = SEC10KParser()
    await parser.fetch_and_parse_all_10k('AAPL')

if __name__ == '__main__':
    asyncio.run(main())