

from abc import ABC, abstractmethod
from typing import Any, Iterator

from langchain_core.language_models.chat_models import BaseChatModel

class Agent(ABC):
    def __init__(self, model:BaseChatModel):
        pass
    @abstractmethod
    def get_response(self, query: str) -> str:
        pass
    @abstractmethod
    def stream_response(self, query: str) -> Iterator[dict[str, Any] | Any]:
        pass    