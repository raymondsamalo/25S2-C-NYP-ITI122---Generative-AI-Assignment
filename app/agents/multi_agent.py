import threading

from langchain.agents import create_agent

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool, tool
from app.langchain.tools import (customer_lookup, interest_rate_for_risk, overall_risk_policy, interest_rate_policy,
                                 overall_risk_policy_lookup, loan_assement)
from app.agents.agent import Agent
from app.langchain.llm import llm_chat


class SpecializedAgent:
    """ A specialized agent with its own model and tools."""

    def __init__(self, model: BaseChatModel, tools: list[BaseTool], system_prompt: str):
        self.agent = create_agent(
            model, tools=tools, system_prompt=system_prompt)
        self.thread_id = str(threading.get_ident())


class LoanMultiAgent(Agent):
    """ An orchestrator agent that manages multiple internal specialized agents for loan risk assessment."""

    def __init__(self, config):
        if config.multi_model:
            customer_data_agent_model = llm_chat(config, temperature=0)
            risk_policy_agent_model = llm_chat(config, temperature=0)
            interest_policy_agent_model = llm_chat(config, temperature=0)
            ochestrator_agent_model = llm_chat(config, temperature=0)
        else:
            shared_model = llm_chat(config, temperature=0)
            customer_data_agent_model = shared_model
            risk_policy_agent_model = shared_model
            interest_policy_agent_model = shared_model
            ochestrator_agent_model = shared_model
        customer_data_agent_prompt = (
            "You are the Customer Data Lookup Agent. "
            """
            You have access to the following tools:
            - customer_lookup: to lookup customer information by identifier which can be customer ID, email, or name.
            """
            "Use the provided tool to retrieve customer profile data such as email, name, ID, credit score, account status, residency. "
            "Only return information from the tool output."
        )
        customer_data_agent = SpecializedAgent(customer_data_agent_model, tools=[
                                               customer_lookup], system_prompt=customer_data_agent_prompt)

        risk_policy_agent_prompt = (
            "You are the Risk Policy Agent. "
            """
            You have access to the following tools:
            - overall_risk_policy_lookup: to lookup overall risk level based on customer's credit score and account status.
            - overall_risk_policy: to provide overall risk policy information of the bank.
            """
            "Use the provided tool to retrieve bank risk policy or determine customer overall risk. "
            "Only return information from the tool output."
        )
        risk_policy_agent = SpecializedAgent(risk_policy_agent_model, tools=[
                                             overall_risk_policy_lookup, overall_risk_policy], system_prompt=risk_policy_agent_prompt)

        interest_policy_agent_prompt = (
            "You are the Interest Rate Policy Agent. "
            """
            You have access to the following tools:
            - interest_rate_policy_lookup: to lookup interest rate percentage based on the customer's overall risk level.
            - interest_rate_policy: to provide interest rate policy information of the bank.
            """
            "Use the provided tool to retrieve bank interest rate policy or determine customer interest rate. "
            "Only return information from the tool output."
        )
        interest_policy_agent = SpecializedAgent(interest_policy_agent_model, tools=[
                                                 interest_rate_for_risk, interest_rate_policy], system_prompt=interest_policy_agent_prompt)

        @tool
        def agent_risk_policy(query: str | dict):
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

    Directives for loan assesment:
    - Always use the loan_assement tool to make loan assesment
    - Display the loan assesment report in a clear manner
    - Display key information like name, residency, account status, credit score, risk level, interest rate
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
        tools = [agent_customer_data, agent_interest_policy,
                 agent_risk_policy, loan_assement]
        super().__init__(ochestrator_agent_model, tools, system_prompt)
