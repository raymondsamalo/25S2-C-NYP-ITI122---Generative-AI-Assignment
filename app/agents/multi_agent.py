from langchain.agents import create_agent
import threading

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool, tool
from app.langchain.tools import (customer_lookup, interest_rate_policy_lookup,
                                 overall_risk_policy_lookup, loan_assement)
from app.agents.agent import Agent


class SpecializedAgent:
    def __init__(self, model: BaseChatModel, tools: list[BaseTool], system_prompt: str):
        self.agent = create_agent(
            model, tools=tools, system_prompt=system_prompt)
        self.thread_id = str(threading.get_ident())


class OchestratorAgent(Agent):

    def __init__(self, model: BaseChatModel):

        customer_data_agent_prompt = (
            "You are the Customer Data Lookup Agent. "
            "Use the provided tool to retrieve customer profile data. "
            "Only return information from the tool output."
        )
        customer_data_agent = SpecializedAgent(model, tools=[customer_lookup], system_prompt=customer_data_agent_prompt)

        risk_policy_agent_prompt = (
            "You are the Risk Policy Agent. "
            "Use the provided tool to retrieve bank risk policy or determine customer overall risk. "
            "Only return information from the tool output."
        )
        risk_policy_agent = SpecializedAgent(model, tools=[overall_risk_policy_lookup], system_prompt=risk_policy_agent_prompt)

        interest_policy_agent_prompt = (
            "You are the Interest Rate Policy Agent. "
            "Use the provided tool to retrieve bank interest rate policy or determine customer interest rate. "
            "Only return information from the tool output."
        )
        interest_policy_agent = SpecializedAgent(model, tools=[interest_rate_policy_lookup], system_prompt=interest_policy_agent_prompt)

        @tool
        def agent_risk_policy(query: str|dict):
            """ handle any query related to determining interest rate given a risk level or bank interest rate policy """
            return risk_policy_agent.agent.invoke(
                {"messages": [{"role": "user", "content": query}]}
            )

        @tool
        def agent_customer_data(query: str):
            """ handle any query related to customer info"""
            return customer_data_agent.agent.invoke(
                {"messages": [{"role": "user", "content": query}]}
            )

        @tool
        def agent_interest_policy(query: str):
            """ handle any query related to determining risk of a customer or bank risk policy """
            return interest_policy_agent.agent.invoke(
                {"messages": [{"role": "user", "content": query}]}
            )

        system_prompt = """
    You are the Supervisor Loan Risk Chatbot.
    
    You speak directly to the user.

    Your role:
    - Understand the user request
    - Decide which agent tool to call
    - Combine results and give a final human-friendly answer
    - If the user is not asking for risk checks, answer conversationally
    - If user ask for customer specific data like email or account status only provide the data that is asked

    When to call tools:
    - If user gives a customer_id or name or email → call agent_customer_data
    - If user asks for risk level -> call agent_risk_policy
    - if user ask for interest rate -> call agent_interest_policy
    - If user asks for bank risk policy -> call agent_risk_policy
    - If user asks for bank interest rate policy -> call agent_interest_policy
    - If user ask for loan assesment  -> call agent_customer_data and pass the info to loan_assement

    If the user provides incomplete or invalid customer identifier,
    inform the user to provide a valid customer ID, email, or name.
    Only return information from the tool output.
    Only make assesment using tool.
    Always:
    - Provide a clear summary, not raw tool output
    - Keep conversation natural and helpful
    - Cite the source of your information from the tools.
    - Explain your reasoning step by step.
    - Summarize your final recommendation clearly.
    - Be concise, professional and polite in your response.
    - Do not assume that user is asking for loan recommendation for a customer unless explicitly asked.
    """
        tools = [agent_customer_data, agent_interest_policy, agent_risk_policy, loan_assement]
        super().__init__(model, tools, system_prompt)
