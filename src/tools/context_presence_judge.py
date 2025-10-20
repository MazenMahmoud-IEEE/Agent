from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from dotenv import load_dotenv
import os
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence

load_dotenv(".env")

def build_context_presence_tool(llm):
    # Get prompt path from environment variable
    prompt_path = os.getenv("PROMPTS_DIR")

    if not prompt_path or not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found at path: {prompt_path}")

    # Load the prompt text
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()

    # Create the prompt template
    prompt = PromptTemplate.from_template(prompt_text)
    
    chain = prompt | llm

    # Define callable that the Tool will use
    def judge_context(query: str) -> str:
        response = chain.invoke({"input": query})
        return response.strip()

    # Return the LangChain Tool
    return Tool.from_function(
        func=judge_context,
        name="ContextPresenceJudge",
        description="Determines if the user provided background context or not."
    )
