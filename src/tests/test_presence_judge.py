from langchain_community.llms import Ollama
from src.tools.context_presence_judge import build_context_presence_tool

# Connect to your local Ollama model
llm = Ollama(
    model="llama3.2:1b",         # exact model name you pulled
    base_url="http://localhost:11434"  # ensures it connects to your local server
)

# Build your custom context presence tool
context_judge = build_context_presence_tool(llm)

# Example test queries
queries = [
    "I was analyzing data from my IoT sensors yesterday. Can you explain how to clean it?",
    "What is data science?"
]

for q in queries:
    print(f"\nQuery: {q}")
    print("Result:", context_judge.run(q))
