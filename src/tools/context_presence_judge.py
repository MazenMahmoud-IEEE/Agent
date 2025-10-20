from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from dotenv import load_dotenv
load_dotenv(".env")

def build_context_presence_tool(llm):
    prompt = PromptTemplate.from_template(
        open('PROMPTS_DIR', "r").read()
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return Tool.from_function(
        func=chain.run,
        name="ContextPresenceJudge",
        description="Determines if user provided background context or not."
    )
