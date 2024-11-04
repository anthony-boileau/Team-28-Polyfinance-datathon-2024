import json
from typing import Dict, Any, List, Union
from singleton_decorator import singleton
import chromadb
from chromadb.config import Settings
from datetime import datetime
import asyncio
import psutil
import statistics
from api import API as api

@singleton
class DBagent:
    def __init__(self):
        """Initialize the DBagent with ChromaDB client."""
        try:
            self._client = chromadb.PersistentClient(
                path="./database",
                settings=Settings(allow_reset=True,
                                anonymized_telemetry=False)
            )
        except Exception as e:
            print(f"Error initializing ChromaDB client: {str(e)}")
            raise

    def __getattr__(self, name):
        """Delegate any unknown attributes/methods to the client."""
        return getattr(self._client, name)

    def format_metadata_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a citation string."""
        return f"{metadata['year']} Annual Report, {metadata['item']}"

    def tokenize_annual_report(self, filepath: str, collection) -> bool:
        """
        Read and process an annual report JSON file and upsert it into the collection.
        
        Args:
            filepath (str): Path to the JSON file containing the annual report
            collection: ChromaDB collection object
        
        Returns:
            bool: True if successful, False if any errors occurred
        """
        try:
            # Read and parse the JSON file
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not all(key in data for key in ['documents', 'metadatas', 'ids']):
                print(f"Invalid JSON format in {filepath}. Missing required keys.")
                return False

            # Validate data lengths match
            if not (len(data['documents']) == len(data['metadatas']) == len(data['ids'])):
                print(f"Mismatched lengths in {filepath} data")
                return False

            # Upsert the data into the collection
            collection.upsert(
                documents=data['documents'],
                metadatas=data['metadatas'],
                ids=data['ids']
            )
            
            print(f"Successfully processed and upserted {filepath}")
            return True

        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return False
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in {filepath}: {str(e)}")
            return False
        except Exception as e:
            print(f"Error processing {filepath}: {str(e)}")
            return False

    async def embed_company_over_daterange(self, ticker: str, fromYear: int, toYear: int = None) -> bool:
        """
        Embed all annual reports for a company within the specified year range.
        
        Args:
            ticker (str): Company ticker symbol
            fromYear (int): Starting year
            toYear (int, optional): Ending year. Defaults to current year if not provided.
        
        Returns:
            bool: True if successful, False if any errors occurred
        """
        if toYear is None:
            toYear = datetime.now().year

        try:
            # Get or create collection for this company
            collection = self.get_or_create_collection(ticker)
            
            # Generate the collections using the API
            api_instance = api()
            success = await api_instance.batch_get_collections(ticker, fromYear, toYear)
            
            if not success:
                print(f"Failed to generate collections for {ticker}")
                return False

            # Process each year's report
            for year in range(fromYear, toYear + 1):
                filepath = f"./json/datadumps/{ticker}-{year}-10k-collection.json"
                if not self.tokenize_annual_report(filepath, collection):
                    print(f"Failed to process {year} for {ticker}")
                    return False

            print(f"Successfully embedded all reports for {ticker} from {fromYear} to {toYear}")
            return True

        except Exception as e:
            print(f"Error embedding company {ticker}: {str(e)}")
            return False

    def get_context(self, prompt: str, fromYear: int, ticker: str, context_vector_count: int = 16) -> str:
        """
        Get context for a given prompt by retrieving and formatting relevant data.
        
        Args:
            prompt: The query prompt
            fromYear: Starting year for the search
            ticker: Stock ticker symbol
            context_vector_count: Number of vectors to retrieve (default: 3)
            
        Returns:
            Formatted context string with retrieved data
        """
        # Get data using the prompt
        data = self.get_data(prompt, fromYear, ticker, context_vector_count)
        
        # Check if we got any results
        if not data['documents'] or not data['documents'][0]:
            return "No relevant data found for the given criteria."
            
        # Create a list to store all content and a set for unique citations
        content_list = []
        citations = set()
        
        # Zip together documents and metadatas from the response
        for docs, metas in zip(data['documents'][0], data['metadatas'][0]):
            # Add the document content
            content_list.append(docs)
            
            # Add the citation to our set
            citations.add(self.format_metadata_citation(metas))
            
        # Join all content into a single paragraph
        content = " ".join(content_list)
        
        # Format citations
        citation_text = "\n\nSources:\n* " + "\n* ".join(sorted(citations))
            

        context = (
            "System: You are a financial analyst specializing in annual report analysis. "
            "Provide essential information in a clear, concise format while maintaining high standards "
            "for accuracy and completeness.\n\n"
            "Response Format:\n"
            "1. Generate a single, well-structured paragraph that synthesizes all the information\n"
            "2. Focus on key facts and maintain objectivity\n"
            "3. Express uncertainty when appropriate\n"
            "4. End with a comprehensive source list\n\n"
            "Content to analyze:\n"
            f"{content}\n"
            f"{citation_text}\n\n"
            "Constraints:\n"
            "- Maximum 5 sentences\n"
            "- Create a cohesive narrative from all sources\n"
            "- Use only factual statements from the sources\n"
            "- Be direct about limitations in the source material\n"
            "- Maintain formal, analytical tone\n"
            "- Do not use any HTML formatting or tags\n"
            "- If content is irrelevant or insufficient, say so rather than making assumptions\n"
            "- Ensure every sentence is complete and ends with proper punctuation\n"
        )
        return context

    def get_data(self, prompt: str, fromYear: int, ticker: str, context_vector_count: int = 16) -> Dict:
        """
        Query the ChromaDB collection for relevant data based on the prompt and parameters.
        
        Args:
            prompt: The query prompt
            fromYear: Starting year for the search
            ticker: Stock ticker symbol
            context_vector_count: Number of vectors to retrieve
            
        Returns:
            Dictionary containing query results from ChromaDB
        """
        collection = self.get_collection(name=ticker)
        
        # Generate list of years from fromYear to current year (inclusive)
        current_year = datetime.now().year
        
        # Handle the case where fromYear is in the future
        if fromYear > current_year:
            fromYear = current_year
            
        # Include the current year in the range
        years = list(range(fromYear, current_year + 1))
        
        # Ensure we have at least one year in the list
        if not years:
            years = [current_year]
            
        # Query the collection with filters
        try:
            data = collection.query(
                query_texts=[prompt],
                n_results=context_vector_count,
                where={
                    "year": {
                        "$in": years
                    }
                },
                include=["documents", "metadatas", "distances"]
            )
            return data
        except Exception as e:
            print(f"Error querying collection: {str(e)}")
            raise
