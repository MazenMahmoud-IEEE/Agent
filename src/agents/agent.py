# src/agents/agent.py
from src.tools.context_presence_judge import ContextPresenceTool
from src.tools.web_search import WebSearchTool
from langchain_community.llms import Ollama

class ContextSearchAgent:
    def __init__(self):
        # Initialize local LLM (sync use)
        self.llm = Ollama(model="llama3.2:1b")

        # Tools (make these classes/funcs return sync data)
        self.context_judge = ContextPresenceTool(self.llm)
        self.web_search = WebSearchTool()

    def format_search_results(self, results):
        """Convert Tavily list of results into a readable string."""
        # ✅ If results is a string (new LangChain behavior)
        if isinstance(results, str):
            return results.strip()

        # ✅ If it's an empty or invalid structure
        if not results or not isinstance(results, list):
            return "No relevant web results found."

        formatted = ""
        for i, item in enumerate(results, start=1):
            title = item.get("title", "No title")
            url = item.get("url", "No URL")
            content = item.get("content", "")[:400]
            formatted += f"{i}. {title}\n{url}\n{content}\n\n"

        return formatted.strip()

    def run(self, query: str):
        try:
            print(f"\n🔍 User Query: {query}")

            # Step 1: Check for context (make sure context_judge.run returns a string or a consistent structure)
            print("🧠 Checking if query has context...")
            context_result = self.context_judge.run(query)
            print(f"Context Judge Output: {context_result}")

            # Normalize decision safely
            decision = ""
            if isinstance(context_result, dict):
                if "clean" in context_result and isinstance(context_result["clean"], dict):
                    decision = context_result["clean"].get("decision", "")
                elif "decision" in context_result:
                    decision = context_result["decision"]
                else:
                    # If tool returns a structured dict, prefer 'decision' or fallback to a text fingerprint
                    decision = str(context_result)
            else:
                decision = str(context_result)

            decision = decision.lower().strip()

            # Step 2: pick behavior
            if "context_missing" in decision or "no_context" in decision or "missing" in decision:
                print("🌐 No context found. Running web search...")
                search_results = self.web_search.run(query)
                
                # Get the inner results list safely
                raw_results = []
                if isinstance(search_results, dict):
                    raw_results = (
                        search_results.get("raw", {}).get("results", [])
                        or search_results.get("clean", {}).get("results", [])
                        or []
                    )
                else:
                    raw_results = search_results

                formatted_results = self.format_search_results(raw_results)

                # 🧠 NEW STEP: Summarize using LLM
                summary_prompt = f"""
                Summarize the following recent web search results into a clear, factual paragraph.
                Focus only on the key facts, dates, and outcomes. Be concise and objective.

                Query: {query}

                Web Results:
                {formatted_results}
                """

                llm_summary = self.llm.invoke(summary_prompt)

                response = {
                    "tool_used": "web_search",
                    "summary": llm_summary,
                    "results": formatted_results
                }
            else:
                print("💬 Context detected. Using local LLM for response...")
                # Ensure use of sync call of LLM; if your LLM API is async, keep to sync wrappers
                llm_response = self.llm.invoke(f"Answer the following query directly with reasoning:\n\n{query}")
                response = {
                    "tool_used": "local_llm",
                    "summary": llm_response
                }

            return {
                "query": query,
                "context_judge_result": decision,
                "agent_response": response
            }

        except Exception as e:
            print(f"❌ Error inside agent.run(): {e}")
            return {"error": str(e)}
