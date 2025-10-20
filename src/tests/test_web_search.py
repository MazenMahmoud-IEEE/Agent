from src.tools.web_search import build_web_search_tool

def main():
    web_tool = build_web_search_tool()

    queries = [
        "latest AI model released by OpenAI 2025",
        "current inflation rate in Egypt 2025"
    ]

    for q in queries:
        print(f"\nQuery: {q}")
        result = web_tool.run(q)
        print("Result:\n", result, "\n")

if __name__ == "__main__":
    main()
