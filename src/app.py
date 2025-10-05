import os
import asyncio
import logging
from dotenv import load_dotenv
from textwrap import dedent
import streamlit as st
from constants import SYSTEM_PROMPT
from core import run_query, load_and_check_env_vars, setup_agent_and_session

from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    AsyncOpenAI,
    SQLiteSession,
)


LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

set_tracing_disabled(disabled=True)




async def process_query(agent: Agent, session: SQLiteSession, query: str):
    """
    Process a user query using the Notia agent and handles UI-specific errors.
    """
    try:
        return await run_query(agent, session, query)
    except Exception as e:
        # The error is already logged by run_query
        return f"An error occurred: {e}"


def main():
    """
    Main function to initialize the Notia agent and start the Streamlit UI.
    """
    missing = load_and_check_env_vars()
    if missing:
        st.error(f"Missing required environment variables: {', '.join(missing)}")
        return

    agent, session = setup_agent_and_session()

    st.title("Notia - Your Second Brain for Development Projects")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome to Notia! How can I help you today?"}
        ]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if query := st.chat_input("Ask Notia anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(query)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = asyncio.run(process_query(agent, session, query))
                st.markdown(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
