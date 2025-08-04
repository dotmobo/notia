# Notia - Your Second Brain for Development Projects

**Notia** is a powerful, command-line-based AI assistant designed to act as a second brain for developers. It helps you manage project-related notes, ideas, tasks, and code snippets seamlessly through a conversational interface.

Leveraging a vector database, Notia allows for intelligent, semantic search across all your notes, making it easy to find information, recall context, and discover connections between your ideas.

---

## Features

- **Conversational Interface**: Interact with your notes in natural language.
- **Intelligent Note Management**: Add, list, and delete notes with simple commands.
- **Semantic Search**: Ask questions and find the most relevant notes, even if the keywords don't match exactly.
- **Persistent Memory**: Notia remembers the context of your conversation for a more natural interaction.
- **Local-First**: All your notes are stored locally in a ChromaDB database.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- An OpenAI-compatible API key and endpoint

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd notia
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the dependencies in editable mode:**
    ```bash
    pip install -e .
    ```

### Configuration

Notia requires the following environment variables to connect to your AI model provider:

```bash
export OPENAI_API_KEY="your_api_key"
export OPENAI_API_BASE="your_api_base_url"
export OPENAI_API_MODEL="your_model_name" # Optional, defaults to "qwen3"
export OPENAI_EMBEDDING_MODEL="your_embedding_model_name"
export OPENAI_RERANK_MODEL="your_rerank_model_name" # Optional, defaults to "bge-reranker"
```

Create a `.env` file or export these variables in your shell before running the application.

## Usage

Once the installation and configuration are complete, you can start the application by simply running:

```bash
notia
```

You will be greeted by the `notia>` prompt. Here are a few examples of what you can do:

- **Add a new note:**
  > `add_note content="I need to refactor the authentication module to use JWT." tags="auth,backend,task"`

- **Search for notes:**
  > `What are the current tasks for the backend?`

- **List all your notes:**
  > `list_all_notes`

- **Delete a note (you need its ID from the list or add command):**
  > `delete_note note_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"`

- **Have a conversation:**
  > `notia> search for notes about authentication`
  > `[...search results...]`
  > `notia> summarize them`

To exit the application, simply type `exit` or `quit`.
