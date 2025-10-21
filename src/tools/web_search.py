# src/tools/web_search.py
import os
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv

from langchain.tools import Tool
# Tavily search class (deprecated warnings possible depending on version)
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


class WebSearchTool:
    """
    Wrap Tavily search as an async-friendly tool returning a standardized response.
    """

    def __init__(self, max_results: int = 5):
        if not TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY not found in environment (.env)")

        self.searcher = TavilySearchResults(max_results=max_results, api_key=TAVILY_API_KEY)

        # Provide a LangChain Tool compat wrapper (sync)
        def _tool_fn(q: str):
            return asyncio.get_event_loop().run_until_complete(self.run_async(q))
        self.tool = Tool.from_function(func=_tool_fn, name="WebSearchTool",
                                       description="Searches the web for up-to-date information using the Tavily API.")

    def _format_results(self, results: List[dict]) -> str:
        lines = []
        for i, r in enumerate(results, start=1):
            title = r.get("title", "No title")
            url = r.get("url", "No url")
            content = r.get("content", "")
            lines.append(f"{i}. {title}\n{url}\n{content[:400]}")  # truncate content for readability
        return "\n\n".join(lines)

    async def run_async(self, query: str) -> Dict[str, Any]:
        # Blocking API call wrapped in to_thread
        def _call():
            return self.searcher.run(query)

        try:
            raw_results = await asyncio.to_thread(_call)
        except Exception as e:
            raw_results = []
            error = str(e)
        else:
            error = None

        # raw_results may be a list of dicts (Tavily format)
        formatted = self._format_results(raw_results) if raw_results else ""

        # create a simple LLM-style summary placeholder to be replaced later if needed
        clean_summary = f"Found {len(raw_results) if raw_results else 0} results for query."

        return {
            "tool": "web_search",
            "query": query,
            "raw": {"results": raw_results, "error": error},
            "clean": {"summary": clean_summary, "snippet": formatted, "sources": [r.get("url") for r in raw_results] if raw_results else []}
        }

    def run(self, query: str) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(self.run_async(query))
