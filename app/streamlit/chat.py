import sys
import os
import streamlit as st
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from app.dependencies import CONFIG
from app.langchain.llm import llm_chat, llm_config_info
from app.agents.single_agent import LoanAgent
from app.agents.multi_agent import OchestratorAgent

class ChatApp:
    def __init__(self) -> None:
        self.llm_info = llm_config_info(CONFIG)
        self.llm = llm_chat(CONFIG)
        if CONFIG.multi_agent:
            self.agent = OchestratorAgent(self.llm)
        else:    
            self.agent = LoanAgent(self.llm)
        
    def setup(self):
        st.set_option("client.toolbarMode", "minimal")
        if "history" not in st.session_state:
            st.session_state.history = []

    def show_title(self):
        title_row = st.container(
            horizontal=True,
            vertical_alignment="bottom",
        )

        with title_row:
            st.title("🏦 Loan Risk Assistant", anchor=False, width="stretch")

    def show_history(self):
        for message in st.session_state.history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def respond(self, user_input):
        # Placeholder for response generation logic
        response = self.agent.get_response(user_input)
        return response

    def has_history(self):
        return "history" in st.session_state and len(st.session_state.history) > 0

    def add_history(self, role, content):
        st.session_state.history.append({"role": role, "content": content})

    def show_intro(self):
        if not self.has_history():
            with st.chat_message("assistant"):
                st.write(f"""Hello 👋 I am a loan assistant running on {self.llm_info}. 
                             I could help to provide customer info, bank risk policy or interest policy and perform loan recomendation analysis
                         """)

    def run(self):
        self.setup()
        self.show_title()
        self.show_intro()
        self.show_history()
        self.main_loop()

    def main_loop(self):
        """ our main loop  """
        prompt = st.chat_input("Say something")
        if prompt:
            with st.chat_message("user"):
                st.write(prompt)
            self.add_history("user", prompt)
            response = self.respond(prompt)
            with st.chat_message("assistant"):
                st.markdown(response)
            self.add_history("assistant", response)


if __name__ == "__main__":
    app = ChatApp()
    app.run()
