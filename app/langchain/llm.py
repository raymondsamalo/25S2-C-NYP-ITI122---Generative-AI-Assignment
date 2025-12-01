from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from pyaml_env import BaseConfig
from langchain_core.language_models.chat_models import BaseChatModel


def llm_chat(config: BaseConfig, temperature=0.1) -> BaseChatModel:
    """
    This is a factory method that return llm chat object
    Args:
        config (BaseConfig): our configuration 
        temperature (float, optional): range from 0 to 1, where 0 is most factual and 1 is most creative.
                         Defaults to 0.1.
    Returns:
        BaseChatModel: our chat model
    """
    if config.model.choice == "groq":
        llm = ChatGroq(model=config.model.groq_model,
                       temperature=temperature)
    else:
        llm = ChatOllama(model=config.model.ollama_model,
                         temperature=temperature)
    return llm

def llm_config_info(config: BaseConfig):
    """ return llm config information"""
    if config.model.choice == "groq":
        model=config.model.groq_model
    else:
        model=config.model.ollama_model
    return f"{config.model.choice} model {model}"