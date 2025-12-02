

import logging
# in subfolder/my_script.py
import threading
import time
from typing import Any, Iterator

from groq import APIError, APIStatusError
from langchain.agents import create_agent
from langchain.messages import AIMessage, AIMessageChunk
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import ValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MAX_RETRIES = 3


class Agent:
    """ Base Agent class wrapping around a LangChain agent with retry logic. """
    def __init__(self, model: BaseChatModel, tools:list[BaseTool], system_prompt:str):
        self.agent = create_agent(
            model, tools=tools, system_prompt=system_prompt, checkpointer=InMemorySaver())
        self.thread_id = str(threading.get_ident())

    def get_response(self, query: str) -> str:
        """ Get response from the agent for the given query. """
        responses = []
        try:
            for retry in range(MAX_RETRIES):
                try:
                    result = self.agent.invoke({"messages": [{"role": "user", "content": query}]},
                                               {"configurable": {"thread_id": self.thread_id}})
                    responses = []
                    for message in result["messages"]:
                        if isinstance(message, AIMessage):
                            responses.append(message.content)
                    break
                except APIStatusError as e:
                    logger.error( "A general API Error occurred: %s on attempt %d/%d. Retrying...", str(e), retry+1, MAX_RETRIES)
                    if e.status_code == 429:
                        return "We run out of tokens for Groq, try again another day"
                    time.sleep(0.2)  # wait before retrying
                except APIError as e:
                    logger.error(
                        "A general API Error occurred: %s on attempt %d/%d. Retrying...", str(e), retry+1, MAX_RETRIES)
                    time.sleep(0.2)  # wait before retrying
        except ValidationError as ve:
            logger.error("Validation Error: %s",ve)
            return "Please rephrase the prompt and try again."
        except Exception as e: 
            logger.error("Unexpected Error: %s",e)
            return f"Unexpected error kindly {str(e)}, feel free to try again."
        return "\n".join(responses)

    def stream(self, query: str) -> Iterator[Any]:
        """ Stream response from the agent for the given query. """
        try:
            for retry in range(MAX_RETRIES):
                try:
                    result = self.agent.stream({"messages": [{"role": "user", "content": query}]},
                                               {"configurable": {"thread_id": self.thread_id}}, stream_mode="messages")
                    for item in result:
                        chunk = item[0]
                        if isinstance(chunk, AIMessageChunk):
                            yield chunk.content
                    break
                except APIError as e:
                    logger.error(
                        "A general API Error occurred: %s on attempt %d/%d. Retrying...", str(e), retry+1, MAX_RETRIES)
                    time.sleep(0.2)  # wait before retrying
        except ValidationError as ve:
            logger.error("Validation Error: %s",ve)
            yield "Please rephrase the prompt and try again."
        except Exception as e:
            logger.error("Unexpected Error: %s",e)
            yield f"Unexpected error kindly {str(e)}, feel free to try again."
