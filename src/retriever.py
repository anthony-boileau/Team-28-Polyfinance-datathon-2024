import json
from typing import Dict, Any, List, Union
from singleton_decorator import singleton

@singleton
class Retriever:
    def __init__(self):
        pass
    
    def format_metadata_citation(self, metadata: Dict[str, Any]) -> str:
        return f"According to the {metadata['year']} annual report of {metadata['ticker']}, {metadata['item']}"
    
    def get_context(self, prompt: str) -> str:
        # Get data using the prompt
        data = self.get_data(prompt)
        
        # Parse JSON data - handle both single and multiple objects
        data_list = json.loads(data)
        if not isinstance(data_list, list):
            data_list = [data_list]
            
        # Format each vector's citation and content
        vector_contexts = []
        for idx, data_dict in enumerate(data_list[:10]):  # Limit to max 10 vectors
            metadata = data_dict["metadata"]
            content = data_dict["content"]
            vector_contexts.append({
                "citation": self.format_metadata_citation(metadata),
                "content": content
            })
        
        context = (
                "System: You are a financial analyst specializing in annual report analysis. "
                "Provide essential information in a structured format while maintaining high standards for accuracy and completeness.\n\n"
                "Response Format:\n"
                "1. For each source, begin with its citation\n"
                "2. For each source's content, state key facts without first person references\n"
                "3. Maintain intellectual honesty - express uncertainty when appropriate\n"
                "4. Complete each thought fully before moving to the next source\n"
                "5. End each statement with appropriate punctuation (.!?)\n\n"
                "Sources to analyze:\n"
                f"{json.dumps(vector_contexts, indent=2)}\n\n"
                "Constraints:\n"
                f"- Maximum of {len(vector_contexts)} sources to analyze\n"
                "- Use 1-3 complete sentences per source\n"
                "- Use only factual statements from the sources\n"
                "- Be direct about limitations in the source material\n"
                "- Maintain formal, analytical tone\n"
                "- If content is irrelevant or insufficient, say so rather than making assumptions\n"
                "- Separate each source's analysis with a line break\n"
                "- Do not use any HTML formatting or tags\n"
                "- Ensure each analysis is complete and doesn't trail off\n"
                "- Every sentence must end with proper punctuation\n"
            )
        return context
    
    def get_data(self, prompt: str) -> str:
        """
        Will eventually be coded to query a db through the prompt.
        Currently returns sample data with multiple vectors.
        """
        sample_data = '''[
            {
                "metadata": {
                    "year": 2020,
                    "ticker": "JAMEIL",
                    "item": "Item 1."
                },
                "content": "Jameil is a food business, we sell breakfast cereal in Algeria"
            },
            {
                "metadata": {
                    "year": 2021,
                    "ticker": "JAMEIL",
                    "item": "Item 1A."
                },
                "content": "The company expanded operations to Morocco and Tunisia. Revenue grew 25% year over year."
            }
        ]'''
        return sample_data


if __name__ == "__main__":
    retriever = Retriever()
    context = retriever.get_context('what is Jameil')
    print(context)