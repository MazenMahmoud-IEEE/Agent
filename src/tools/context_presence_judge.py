# src/tools/context_presence_judge.py
import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from langchain.tools import Tool

load_dotenv()

PROMPTS_DIR = os.getenv("PROMPTS_DIR")


class ContextPresenceTool:
    """
    Wraps a simple LLM-based context presence check.
    Provides both sync `run` (for LangChain Tool compatibility) and async `run_async`.
    """

    def __init__(self, llm):
        if not PROMPTS_DIR or not os.path.exists(PROMPTS_DIR):
            raise FileNotFoundError(f"Prompt file not found at path: {PROMPTS_DIR}")

        with open(PROMPTS_DIR, "r", encoding="utf-8") as f:
            prompt_text = f.read()

        self.prompt = PromptTemplate.from_template(prompt_text)
        # Build a RunnableSequence: prompt | llm
        self.chain = self.prompt | llm

        # Build a LangChain Tool for agent usage (optional)
        def _tool_fn(query: str) -> str:
            # keep old synchronous behavior for Tool.from_function
            return asyncio.get_event_loop().run_until_complete(self.run_async(query))
        self.tool = Tool.from_function(func=_tool_fn, name="ContextPresenceJudge",
                                       description="Determines if the user provided background context or not.")

    async def run_async(self, query: str) -> Dict[str, Any]:
        """Run the chain in a thread-safe way and return a structured response."""
        # perform the blocking invoke in a thread
        def _invoke():
            # chain.invoke expects a mapping for prompt variables
            return self.chain.invoke({"input": query})

        raw_output = await asyncio.to_thread(_invoke)
        raw_text = raw_output.strip() if isinstance(raw_output, str) else str(raw_output)

        # Attempt to normalize into either "context_provided" or "context_missing"
        normalized = raw_text.lower()
        if "context_provided" in normalized or "provided" in normalized:
            clean = {"decision": "context_provided", "extracted": raw_text}
        elif "context_missing" in normalized or "missing" in normalized:
            clean = {"decision": "context_missing", "extracted": raw_text}
        else:
            # Default to missing if unsure
            clean = {"decision": "context_missing", "extracted": raw_text}

        return {
            "tool": "context_presence_judge",
            "query": query,
            "raw": {"llm_raw": raw_text},
            "clean": clean
        }

    def run(self, query: str) -> Dict[str, Any]:
        """Synchronous helper (keeps compatibility with Tool.run style)."""
        return asyncio.get_event_loop().run_until_complete(self.run_async(query))
