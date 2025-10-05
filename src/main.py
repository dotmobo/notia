import os
import asyncio
import logging
from dotenv import load_dotenv
from textwrap import dedent
from constants import SYSTEM_PROMPT
from core import run_query, load_and_check_env_vars, setup_agent_and_session
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




async def process_query(agent: Agent, session: SQLiteSession, query: str):
    """
    Process a user query using the Notia agent and prints the output to the console.
    """
    try:
        response = await run_query(agent, session, query)
        console.print(response)
    except Exception:
        # The error is already logged by run_query
        console.print("[bold red]An error occurred while processing your request.[/bold red]")


async def main():
    """
    Main function to initialize the Notia agent and start the interactive loop.
    It sets up the agent with the OpenAI model and tools, and handles user input.
    """
    agent, session = setup_agent_and_session()

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
    missing = load_and_check_env_vars()
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    asyncio.run(main())
