import os
import asyncio
import logging
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled, AsyncOpenAI, SQLiteSession
from tools import tools
from rich.console import Console

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

set_tracing_disabled(disabled=True)

# Vérifie la présence des variables d'environnement requises
required_env_vars = ["OPENAI_API_KEY", "OPENAI_API_BASE"]
missing = [var for var in required_env_vars if var not in os.environ]
if missing:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

# Instanciation du modèle
model = OpenAIChatCompletionsModel(
    model=os.getenv("OPENAI_API_MODEL", "qwen3"), # Utilise "qwen3" par défaut si non spécifié
    openai_client=AsyncOpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
)

SYSTEM_PROMPT = (
    "/no_think"
    "You are Notia, a powerful AI assistant designed to be a developer's second brain. "
    "Your purpose is to help manage project-related notes, ideas, tasks, and code snippets. "
    "You have access to a set of tools to add, list, delete, and search notes in a vector database. "
    "Be helpful, concise, and proactive. When a user asks a question, use your search tool to find the most relevant notes to answer it."
)

console = Console()

async def process_query(agent: Agent, session: SQLiteSession, query: str):
    """Traite une requête utilisateur de manière asynchrone."""
    try:
        response = await Runner.run(agent, query, session=session)
        console.print(response.final_output)
    except Exception as e:
        LOG.exception(f"Error during query processing: {e}")

async def main():
    """Boucle interactive principale de Notia."""
    agent = Agent(name="Notia", model=model, tools=tools, instructions=SYSTEM_PROMPT)
    session = SQLiteSession("notia")

    console.print("[bold green]Welcome to Notia! Your second brain for development projects.[/bold green]")
    console.print("Type 'exit' or 'quit' to end the session.")

    while True:
        try:
            query = console.input("\n[bold cyan]notia>[/bold cyan] ")

            if query.lower() in ["exit", "quit"]:
                console.print("[bold red]Goodbye![/bold red]")
                break

            await process_query(agent, session, query)

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Goodbye![/bold red]")
            break

def cli():
    """Point d’entrée CLI pour pyproject.toml"""
    asyncio.run(main())
