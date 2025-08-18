import os
import asyncio
import logging
from dotenv import load_dotenv
from textwrap import dedent
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML

from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    AsyncOpenAI,
    SQLiteSession,
)
from console import console

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
        None
    """
    try:
        response = await Runner.run(agent, query, session=session)
        console.print(response.final_output)
    except Exception as e:
        LOG.exception(f"Error during query processing: {e}")


async def main():
    """
    Main function to initialize the Notia agent and start the interactive loop.
    It sets up the agent with the OpenAI model and tools, and handles user input.
    """
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

    session_prompt = PromptSession()

    console.print(
        "[bold green]Welcome to Notia! Your second brain for development projects.[/bold green]"
    )
    console.print("Type 'exit' or 'quit' to end the session.")

    while True:
        try:
            query = await session_prompt.prompt_async(
                HTML("<ansicyan><b>notia></b></ansicyan> ")
            )

            if query.lower() in ["exit", "quit"]: # or CTRL+D
                console.print("[bold red]Goodbye![/bold red]")
                break

            await process_query(agent, session, query)

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Goodbye![/bold red]")
            break


def cli():
    """
    Entrypoint to the Notia CLI.
    Checks for required environment variables and starts the main loop.
    """

    load_dotenv()

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
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    asyncio.run(main())
