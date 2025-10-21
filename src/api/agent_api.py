# src/api/agent_api.py
from fastapi import APIRouter
from pydantic import BaseModel
from src.agents.agent import ContextSearchAgent
import asyncio
import threading

router = APIRouter()
agent = ContextSearchAgent()


class AgentQuery(BaseModel):
    query: str


@router.post("/agent")
def run_agent(input: AgentQuery):
    """
    Synchronous, thread-safe endpoint.
    Ensures an asyncio event loop exists in the current worker thread
    (fixes: "There is no current event loop in thread 'AnyIO worker thread'.")
    """
    try:
        print(f"🔹 Received query: {input.query}")

        got_loop = True
        try:
            # If a running loop exists, great — do nothing.
            asyncio.get_running_loop()
        except RuntimeError:
            # No loop in this thread: create one and set it for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            got_loop = False  # we created it (so we must clean it up after)

        try:
            # Call the synchronous agent.run (the agent/tool code should be sync)
            result = agent.run(input.query)
        finally:
            # If we created the loop here, remove it to avoid leaking it into the thread pool
            if not got_loop:
                try:
                    loop = asyncio.get_event_loop()
                    asyncio.set_event_loop(None)
                    loop.close()
                except Exception:
                    # best-effort cleanup; print for debugging if needed
                    print("⚠️ Warning: failed to cleanup event loop in worker thread")

        print("✅ Response generated successfully")
        return result

    except Exception as e:
        print(f"❌ Error in /agent: {e}")
        return {"error": str(e)}
