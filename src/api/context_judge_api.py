from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from langchain_community.llms import Ollama  # or your local llm wrapper
import os

from src.tools.context_presence_judge import ContextPresenceTool

router = APIRouter()

# lazily initialize LLM & tool
_llm = None
_tool = None


def get_tool() -> ContextPresenceTool:
    global _llm, _tool
    if _tool is None:
        # configure Ollama to your local server if needed via base_url param
        _llm = Ollama(model=os.getenv("LOCAL_LLM_MODEL", "llama3.2:1b"),
                      base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
        _tool = ContextPresenceTool(llm=_llm)
    return _tool


@router.get("/context_judge", summary="Determine if user input contains context")
async def context_judge(query: str = Query(..., description="User input to judge")) -> Dict[str, Any]:
    tool = get_tool()
    try:
        result = await tool.run_async(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result
