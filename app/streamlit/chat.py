import streamlit as st

class ChatApp:
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
            st.title("Loan Risk Assistant",anchor=False,width="stretch")

    def show_history(self):
        for message in st.session_state.history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def respond(self, user_input):
        # Placeholder for response generation logic
        return f"This is a placeholder response. {user_input}"
    
    def add_history(self, role, content):
        st.session_state.history.append({"role": role, "content": content})
    
    def run(self):
        self.setup()
        self.show_title()
        self.show_history()
        with st.chat_message("assistant"):
            st.write("Hello 👋")
        self.main_loop()

    def main_loop(self):
        prompt = st.chat_input("Say something")
        if prompt:
            with st.chat_message("user"):
                st.write(prompt)
            self.add_history("user", prompt)

            response = self.respond(prompt)
            with st.chat_message("assistant"):
                st.markdown(response)
            self.add_history("user", prompt)

if __name__ == "__main__":
    app = ChatApp()
    app.run()
