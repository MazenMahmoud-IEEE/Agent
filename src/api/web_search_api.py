from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import os
from src.tools.web_search import WebSearchTool

router = APIRouter()

_tool = None


def get_tool() -> WebSearchTool:
    global _tool
    if _tool is None:
        _tool = WebSearchTool(max_results=int(os.getenv("WEB_MAX_RESULTS", "5")))
    return _tool


@router.get("/web_search", summary="Run web search via Tavily")
async def web_search(query: str = Query(..., description="Search query")) -> Dict[str, Any]:
    tool = get_tool()
    try:
        result = await tool.run_async(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result
