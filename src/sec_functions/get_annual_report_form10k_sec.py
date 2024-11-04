import aiohttp
import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import logging
from functools import wraps
from bs4 import BeautifulSoup
import re
from singleton_decorator import singleton

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

@singleton
class SEC10KParser:
    def __init__(self) -> None:
        """Initialize the SEC10KParser instance."""
        self.headers: Dict[str, str] = {
            'User-Agent': 'Hackathon polyfinancedatathon2.jp0rh@passmail.net',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive'
        }
        
        # Load form 10-K items from JSON file
        try:
            with open('./json/reference/form-10k-items.json', 'r') as f:
                self.items_map = json.load(f)
        except Exception as e:
            logger.error(f"Error loading form-10k-items.json: {str(e)}")
            raise

    def clean_html_content(self, content: str) -> str:
        """Clean HTML content and normalize whitespace."""
        soup = BeautifulSoup(content, 'html.parser')
        for element in soup(['script', 'style']):
            element.decompose()
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def split_into_chunks(self, text: str, target_words: int = 32) -> List[str]:
        """
        Split text into chunks of approximately target_words length, ending at the nearest period.
        
        Args:
            text (str): The input text to split
            target_words (int): Target number of words per chunk
            
        Returns:
            List[str]: List of text chunks
        """
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            if current_word_count + sentence_words <= target_words:
                current_chunk.append(sentence)
                current_word_count += sentence_words
            else:
                # If we have accumulated sentences, join them and add to chunks
                if current_chunk:
                    chunks.append(' '.join(current_chunk).strip())
                # Start new chunk with current sentence
                current_chunk = [sentence]
                current_word_count = sentence_words
        
        # Add any remaining sentences
        if current_chunk:
            chunks.append(' '.join(current_chunk).strip())
            
        return chunks

    def find_key_positions(self, text: str, key: str) -> List[int]:
        """Find both occurrences of a key in text (TOC and content)."""
        escaped_key = re.escape(key)
        matches = list(re.finditer(escaped_key, text, re.IGNORECASE))
        return [match.start() for match in matches]

    def get_next_key_position(self, text: str, current_key: str, start_pos: int) -> Optional[int]:
        """Find the next key's position, trying multiple subsequent keys if necessary."""
        keys = list(self.items_map.keys())
        current_idx = keys.index(current_key)
        
        # Try the next 3 keys
        for idx in range(current_idx + 1, min(current_idx + 4, len(keys))):
            next_key = keys[idx]
            positions = self.find_key_positions(text, next_key)
            valid_positions = [pos for pos in positions if pos > start_pos]
            if valid_positions:
                return min(valid_positions)
        return None

    def parse_items(self, ticker: str, year: int, text: str) -> Dict:
        """Parse items and return structured data with chunked contents array."""
        clean_text = self.clean_html_content(text)
        
        doc_structure = {
            "ticker": ticker,
            "year": year,
            "items": []
        }
        
        for key in self.items_map:
            positions = self.find_key_positions(clean_text, key)
            
            if positions:  # Check if we found any occurrences
                content_start = positions[-1]  # Get the last occurrence
                content_end = self.get_next_key_position(clean_text, key, content_start)
                
                content = (clean_text[content_start:content_end] if content_end 
                          else clean_text[content_start:]).strip()
                
                # Split content into chunks
                content_chunks = self.split_into_chunks(content)
                
                doc_structure["items"].append({
                    "item": key,
                    "description": self.items_map[key],
                    "contents": content_chunks  # Now an array of chunks named 'contents'
                })
                
                logger.info(f"Successfully parsed {key} for {ticker} {year}")
            else:
                logger.warning(f"No occurrences found for {key}")
        
        return doc_structure

    def extract_filing_data(self, submission_data: Dict, from_year: int, to_year: Optional[int] = None) -> List[Tuple[str, str]]:
        """Extract links and acceptance dates from submission data within the specified year range."""
        if to_year is None:
            to_year = datetime.now().year

        recent_data = submission_data.get('filings', {}).get('recent', {})
        links = recent_data.get('primaryDocumentLinks', [])
        acceptance_dates = recent_data.get('acceptanceDateTime', [])
        
        # Filter by year range
        filtered_data = []
        for link, date in zip(links, acceptance_dates):
            year = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").year
            if from_year <= year <= to_year:
                filtered_data.append((link, date))
        
        return filtered_data

    @rate_limit()
    async def fetch_single_10k(self, ticker: str, filing_data: Tuple[str, str], i: int, total: int) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Fetch and parse a single 10-K document."""
        try:
            link, acceptance_date = filing_data
            async with aiohttp.ClientSession() as session:
                async with session.get(link, headers=self.headers, allow_redirects=True) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch 10-K document {i+1}/{total} for {ticker}.")
                        return False, None, None
                    
                    content = await response.text()
                    year = datetime.strptime(acceptance_date, "%Y-%m-%dT%H:%M:%S.%fZ").year
                    
                    # Parse items and return structured data
                    doc_structure = self.parse_items(ticker, year, content)
                    
                    return True, str(year), doc_structure
                    
        except Exception as e:
            logger.error(f"Error processing link for {ticker}: {str(e)}")
            return False, None, None

    async def fetch_and_parse_all_10k_in_range(self, ticker: str, from_year: int, to_year: Optional[int] = None) -> bool:
        """
        Fetch and parse all 10-K documents for a ticker within the specified year range.
        Returns the parsed data and writes it to files.
        """
        try:
            if to_year is None:
                to_year = datetime.now().year
                
            if from_year > to_year:
                logger.error(f"Invalid year range: from_year ({from_year}) is greater than to_year ({to_year})")
                return False

            # Read submission data
            submission_file = f"./json/datadumps/{ticker}_submissions.json"
            with open(submission_file, 'r') as f:
                submission_data = json.load(f)

            # Extract filing data within date range
            filing_data = self.extract_filing_data(submission_data, from_year, to_year)
            if not filing_data:
                logger.info(f"No filing data found for {ticker} between {from_year} and {to_year}")
                return True

            # Create tasks for parallel processing
            tasks = []
            for i, filing_tuple in enumerate(filing_data):
                task = asyncio.create_task(
                    self.fetch_single_10k(ticker, filing_tuple, i, len(filing_data))
                )
                tasks.append(task)

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and write to files
            for result in results:
                if isinstance(result, tuple) and result[0] and result[2]:
                    year = result[1]
                    doc_structure = result[2]
                    
                    output_filename = f"{ticker}-{year}-10k.json"
                    output_path = f"./json/datadumps/{output_filename}"
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(doc_structure, f, indent=2, ensure_ascii=False)
            
            success = all(isinstance(r, tuple) and r[0] for r in results)
            if success:
                logger.info(f"Successfully processed all 10-K documents for {ticker} between {from_year} and {to_year}")
            else:
                logger.warning(f"Some 10-K documents failed to process for {ticker}")
            
            return success

        except Exception as e:
            logger.error(f"Error in fetch_and_parse_10k for {ticker}: {str(e)}")
            return False

async def main():
    parser = SEC10KParser()
    # Or specify both years
    await parser.fetch_and_parse_all_10k_in_range('MA', from_year=2016)

if __name__ == '__main__':
    asyncio.run(main())