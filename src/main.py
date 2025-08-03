import os
import asyncio
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled, AsyncOpenAI
from agents.extensions.models.litellm_model import LitellmModel
from tools import tools
import logging

LOG = logging.getLogger(__name__)

set_tracing_disabled(disabled=True)


if "OPENAI_API_KEY" not in os.environ or "OPENAI_API_MODEL" not in os.environ or "OPENAI_API_BASE" not in os.environ:
    raise ValueError("Please set the OPENAI_API_KEY, OPENAI_API_MODEL, and OPENAI_API_BASE environment variables.")

# model = LitellmModel(
#     model="hosted_vllm/" + os.getenv("OPENAI_API_MODEL"),
#     base_url=os.getenv("OPENAI_API_BASE"),
#     api_key=os.getenv("OPENAI_API_KEY"),
# )

model = OpenAIChatCompletionsModel(
    model=os.getenv("OPENAI_API_MODEL"),
    openai_client=AsyncOpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
)

SYSTEM_PROMPT = ("You are Notia, a powerful AI assistant designed to be a developer's second brain. "
                 "Your purpose is to help manage project-related notes, ideas, tasks, and code snippets. "
                 "You have access to a set of tools to add, list, delete, and search notes in a vector database. "
                 "Be helpful, concise, and proactive. When a user asks a question, use your search tool to find the most relevant notes to answer it.")

async def notia():
    """Main asynchronous function to run the Notia agent."""
    agent = Agent(name="Notia", model=model, tools=tools, instructions=SYSTEM_PROMPT)

    print("Welcome to Notia! Your second brain for development projects.")
    print("Type 'exit' or 'quit' to end the session.")

    while True:
        try:
            query = input("\nnotia> ")

            if query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            # The runner handles the interaction with the agent asynchronously.
            response = await Runner.run(agent, query)
            print(response.final_output)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    """Synchronous entry point to run the Notia agent."""
    asyncio.run(notia())

if __name__ == "__main__":
    main()