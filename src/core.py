import logging
import os
from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession, OpenAIChatCompletionsModel, AsyncOpenAI
from constants import SYSTEM_PROMPT

LOG = logging.getLogger(__name__)

async def run_query(agent: Agent, session: SQLiteSession, query: str) -> str:
    """
    Runs the query using the agent and returns the final output.
    
    Args:
        agent (Agent): The Notia agent instance.
        session (SQLiteSession): The session for database interactions.
        query (str): The user query to process.

    Returns:
        The response from the agent as a string.
        
    Raises:
        Exception: If an error occurs during query processing.
    """
    try:
        response = await Runner.run(agent, query, session=session)
        return response.final_output
    except Exception as e:
        LOG.exception(f"Error during query processing: {e}")
        # Re-raise the exception to be handled by the caller
        raise

def load_and_check_env_vars():
    """Loads environment variables and checks for missing required ones."""
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
    return missing

def setup_agent_and_session():
    """Initializes and returns the Agent and SQLiteSession."""
    from tools import tools  # Keep this import here as it depends on env vars

    model = OpenAIChatCompletionsModel(
        model=os.getenv("OPENAI_API_MODEL", "qwen3"),
        openai_client=AsyncOpenAI(
            base_url=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
    )
    agent = Agent(name="Notia", model=model, tools=tools, instructions=SYSTEM_PROMPT)
    session = SQLiteSession("notia")
    return agent, session