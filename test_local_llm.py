from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from app.dependencies import CONFIG
from app.dependencies import customer_info_service, db, customer_residency_status_service, customer_credit_score_service, policy_service, customer_account_status_service
model = CONFIG.model.version
#response = ollama.generate(model=model, prompt='Why is the sky blue?')
#print(response['response'])

@tool
def get_customer_id_by_name(name:str)->str:
    """ Get the customer ID for a customer name

    Args:
        name (str): customer name

    Returns:
    """
    customer=customer_info_service.find_by_name(name)
    if customer is None:
        return "not available"
    return str(customer.ID)
@tool
def add(a: int, b: int) -> int:
    """Adds two numbers together""" # this docstring gets used as the description
    return a + b # the actions our tool performs
if __name__ == "__main__":
    # Initialize your Ollama model
    llm = ChatOllama(model=model)

    # Bind the tool to the LLM
    llm_with_tools = llm.bind_tools([get_customer_id_by_name, add])
    response = llm_with_tools.invoke("what is 1 + 2")
    print(response.content)

    # Example interaction where the model doesn't need the tool
    response_no_tool = llm_with_tools.invoke("Tell me a joke.")
    print(response_no_tool.content)
