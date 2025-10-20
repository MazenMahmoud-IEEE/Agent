from src.tools.context_presence_judge import build_context_presence_tool
from src.tools.web_search import build_web_search_tool
from langchain_community.llms import Ollama


class ContextSearchAgent:
    def __init__(self):
        # Initialize local LLM
        self.llm = Ollama(model="llama3.2:1b")

        # Tools
        self.context_judge = build_context_presence_tool(self.llm)
        self.web_search = build_web_search_tool()

    def format_search_results(self, results):
        """Convert Tavily list of results into a readable string."""
        if not results:
            return "No relevant web results found."

        formatted = ""
        for i, item in enumerate(results, start=1):
            title = item.get("title", "No title")
            url = item.get("url", "No URL")
            content = item.get("content", "")[:400]  # shorten long text
            formatted += f"{i}. {title}\n{url}\n{content}\n\n"
        return formatted.strip()

    def run(self, query: str):
        """Main agent logic"""
        print(f"\n🔍 User Query: {query}")

        # Step 1: Check for context
        print("🧠 Checking if query has context...")
        context_result = self.context_judge.run(query)
        print(f"Context Judge Output: {context_result}")

        # Step 2: If missing, use web search
        if "context_missing" in context_result.lower():
            print("🌐 No context found. Running Tavily web search...")
            search_results = self.web_search.run(query)

            formatted_results = self.format_search_results(search_results)
            print(f"🔎 Web Search Results:\n{formatted_results[:500]}...")

            response = (
                "Based on the latest web search results, here's a summary:\n\n"
                + formatted_results
            )
        else:
            # Use local LLM directly
            print("💬 Context detected. Using local LLM for response...")
            response = self.llm.invoke(
                f"Answer the following query directly with reasoning:\n\n{query}"
            )

        return response


if __name__ == "__main__":
    agent = ContextSearchAgent()
    while True:
        user_input = input("\n💬 Enter your query (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            print("👋 Exiting agent. Goodbye!")
            break
        output = agent.run(user_input)
        print(f"\n🧾 Agent Response:\n{output}\n")
