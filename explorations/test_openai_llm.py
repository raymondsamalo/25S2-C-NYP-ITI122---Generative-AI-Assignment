from langchain_openai import ChatOpenAI
from langchain_classic.schema import HumanMessage
import os
from app.dependencies import CONFIG, CONFIG_MAP
OPENAI_API_KEY=CONFIG.model.openai_api_key
print(CONFIG_MAP)
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.9, api_key=OPENAI_API_KEY)


#Test the LLM
print(llm.invoke([{'role':'user', 'content':'Which is the largest country by area in the world?'}]).content)