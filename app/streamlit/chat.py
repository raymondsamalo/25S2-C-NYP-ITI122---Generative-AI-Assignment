import sys
import os
import streamlit as st
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from app.dependencies import CONFIG
from app.langchain.llm import llm_chat, llm_config_info
from app.agents.single_agent import LoanAgent
from app.agents.multi_agent import LoanMultiAgent

class ChatApp:
    def __init__(self) -> None:
        self.llm_info = llm_config_info(CONFIG)
        self.multi_agent = CONFIG.multi_agent
        if self.multi_agent:
            self.agent = LoanMultiAgent(config=CONFIG)
        else:    
            self.agent = LoanAgent(config=CONFIG)
        
    def setup(self):
        st.set_option("client.toolbarMode", "minimal")
        if "history" not in st.session_state:
            st.session_state.history = []
        if 'processing' not in st.session_state:
            st.session_state.processing = False
        if 'prompt' not in st.session_state:
            st.session_state.prompt = ''

    def show_title(self):
        title_row = st.container(
            horizontal=True,
            vertical_alignment="bottom",
        )
        if self.multi_agent:
            architecture="Multi Agents"
        else:
            architecture="Simple Agent"
        with title_row:
            st.title("🏦 Loan Risk Assistant", anchor=False, width="stretch")
        st.subheader(f"💬  {architecture} Powered by {self.llm_info}")

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
                st.write("""Hello 👋 I am a loan assistant.
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
        if prompt := st.chat_input("Say something", disabled=st.session_state.processing):
            st.session_state.processing = True
            st.session_state.prompt = prompt
            self.add_history("user", prompt)
            st.rerun() # Rerun to disable the chat_input immediately
        if st.session_state.processing:
            # Simulate AI response generation
            #with st.spinner("Generating response..."):
            #    prompt = st.session_state.prompt
            #    response = self.respond(prompt)
            #with st.chat_message("assistant"):
            #    st.markdown(response)
            with st.spinner("Generating response..."):
                with st.chat_message("assistant"):
                    response=st.write_stream(self.agent.stream(st.session_state.prompt))
                    self.add_history("assistant", response)
            st.session_state.processing = False
            st.rerun() # Rerun to display assistant's message and re-enable chat_input
        

if __name__ == "__main__":
    app = ChatApp()
    app.run()
