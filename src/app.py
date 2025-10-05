import os
import asyncio
import logging
from dotenv import load_dotenv
from textwrap import dedent
import streamlit as st

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

SYSTEM_PROMPT = dedent("""
    /no_think
    You are Notia, a powerful AI assistant designed to be a developer's second brain.
    Your purpose is to help manage project-related notes, ideas, tasks, and code snippets.
    You have access to a set of tools to add, list, delete, and search notes in a vector database.
    Be helpful, concise, and proactive. When a user asks a question, use your search tool to find the most relevant notes to answer it.
    Pay close attention to the 'Rerank Score' provided by the search tool; a higher score indicates greater relevance to the query.
""")


async def process_query(agent: Agent, session: SQLiteSession, query: str):
    """
    Process a user query using the Notia agent.

    Args:
        agent (Agent): The Notia agent instance.
        session (SQLiteSession): The session for database interactions.
        query (str): The user query to process.

    Returns:
        The response from the agent.
    """
    try:
        response = await Runner.run(agent, query, session=session)
        return response.final_output
    except Exception as e:
        LOG.exception(f"Error during query processing: {e}")
        return f"An error occurred: {e}"


def main():
    """
    Main function to initialize the Notia agent and start the Streamlit UI.
    """
    load_dotenv()

    # Check for required environment variables
    missing = [
        var
        for var in [
            "OPENAI_API_KEY",
            "OPENAI_API_BASE",
            "OPENAI_EMBEDDING_MODEL",
            "OPENAI_RERANK_MODEL",
        ]
        if var not in os.environ
    ]
    if missing:
        st.error(f"Missing required environment variables: {', '.join(missing)}")
        return

    from tools import tools  # Import tools after settings of the environment variables

    model = OpenAIChatCompletionsModel(
        model=os.getenv("OPENAI_API_MODEL", "qwen3"),
        openai_client=AsyncOpenAI(
            base_url=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
    )

    agent = Agent(name="Notia", model=model, tools=tools, instructions=SYSTEM_PROMPT)
    session = SQLiteSession("notia")

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
