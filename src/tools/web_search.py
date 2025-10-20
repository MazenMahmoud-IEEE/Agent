from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import Tool
from dotenv import load_dotenv
import os

load_dotenv(".env")

def build_web_search_tool():
    """Builds the Tavily web search tool."""
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY not found in .env file")

    # Initialize the Tavily search tool
    tavily_search = TavilySearchResults(
        max_results=5,
        api_key=tavily_api_key
    )

    # Wrap it as a LangChain Tool
    return Tool.from_function(
        func=tavily_search.run,
        name="WebSearchTool",
        description="Searches the web for up-to-date information using the Tavily API."
    )
