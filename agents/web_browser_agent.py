from .base import BaseAgent
from airis.llm import LLMClient
import requests
from bs4 import BeautifulSoup
import re

class WebBrowserAgent(BaseAgent):
    """
    Agent that fetches content from a URL and summarizes it.
    """
    def __init__(self):
        self.llm_client = LLMClient()

    def _extract_url(self, instruction: str) -> str | None:
        """Extracts the first URL from an instruction using regex."""
        # A simple regex to find the first http/https URL
        match = re.search(r'https?://[\w\-./?=&]+', instruction)
        return match.group(0) if match else None

    def _fetch_and_parse(self, url: str) -> str:
        """Fetches a URL and extracts clean text content."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # Raise an exception for bad status codes

            soup = BeautifulSoup(response.text, 'lxml')

            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # Limit the text to a reasonable length for the LLM context
            max_length = 8000
            return text[:max_length]

        except requests.RequestException as e:
            return f"Error fetching URL: {e}"

    def execute(self, instruction: str, context: str | None = None, **kwargs) -> str:
        """
        Extracts a URL from an instruction or context, fetches its content, and provides a summary.
        """
        print(f"--- WebBrowserAgent received instruction: '{instruction}' ---")
        
        # Combine instruction and context to find a URL
        text_to_search = instruction + "\n" + (context or "")
        url = self._extract_url(text_to_search)

        if not url:
            return "Error: No URL found in the instruction."

        print(f"--- WebBrowserAgent fetching content from: {url} ---")
        content = self._fetch_and_parse(url)

        if content.startswith("Error:"):
            return content

        summary_prompt = f"""
        Based on the following text from the webpage {url}, provide a concise summary that addresses the user's original instruction.

        Original Instruction: "{instruction}"

        Webpage Text:
        ---
        {content}
        ---
        """

        print("--- WebBrowserAgent summarizing content... ---")
        summary = self.llm_client.invoke(summary_prompt)
        return summary.content
