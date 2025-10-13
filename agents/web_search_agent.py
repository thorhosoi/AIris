from .base import BaseAgent
from airis.llm import LLMClient
from ddgs import DDGS

class WebSearchAgent(BaseAgent):
    """
    Agent that performs a web search using DuckDuckGo.
    """
    def __init__(self):
        self.llm_client = LLMClient()

    def execute(self, instruction: str, context: str | None = None, **kwargs) -> str:
        """
        Performs a web search based on the instruction and context, then returns a summary.
        """

        prompt = f"""
        You are an expert at crafting search engine queries. 
        Based on the user's instruction and the context from the previous turn, generate the most effective possible search query.
        Only output the search query itself, with no explanation or extra text.

        Previous Turn's Context:
        ---
        {context or 'No previous context.'}
        ---

        Current User Instruction: "{instruction}"
        """
        
        query = self.llm_client.invoke(prompt).content.strip()

        try:
            with DDGS() as ddgs:
                # max_results=5 to keep it concise
                results = list(ddgs.text(query, max_results=5))
            
            if not results:
                return "No search results found."

            # Format the results for the summarization prompt
            results_text = ""
            for i, result in enumerate(results):
                results_text += f"Result {i+1}:\n"
                results_text += f"  Title: {result.get('title')}\n"
                results_text += f"  Snippet: {result.get('body')}\n"
                results_text += f"  URL: {result.get('href')}\n\n"

            summary_prompt = f"""
            Based on the following web search results, provide a concise answer to the original instruction.
            Synthesize the information from the snippets into a coherent response.

            Original Instruction: "{instruction}"

            Search Results:
            {results_text}
            """

            summary = self.llm_client.invoke(summary_prompt)
            return summary.content

        except Exception as e:
            return f"Error during web search or summarization: {e}"
