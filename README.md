<p align="center">
  <img src="logo.png" alt="Notia Logo" width="170"/>
</p>
<h1 align="center">Notia - Your Second Brain for Development Projects</h1>

**Notia** is a powerful AI assistant designed to act as a second brain for developers. It helps you manage project-related notes, ideas, tasks, and code snippets seamlessly through a conversational interface, available both as a command-line tool and a web application.

Leveraging a vector database, Notia allows for intelligent, semantic search across all your notes, making it easy to find information, recall context, and discover connections between your ideas.

## Features

- **Conversational Interface**: Interact with your notes in natural language.
- **Web Interface**: An intuitive web-based UI built with Streamlit for a more visual interaction.
- **Intelligent Note Management**: Add, list, and delete notes with simple commands.
- **Semantic Search**: Ask questions and find the most relevant notes, even if the keywords don't match exactly.
- **Persistent Memory**: Notia remembers the context of your conversation for a more natural interaction.
- **Local-First**: All your notes are stored locally in a ChromaDB database.
- **High-Performance Analysis**: Leverage Rust for fast and efficient data processing on your notes.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Rust and Cargo (install via https://rustup.rs/)
- An OpenAI-compatible API key and endpoint with a chat model, an embedding model, and a reranking model

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

4.  **Build the Rust analysis module:**
    ```bash
    cd rust_analyzer && maturin develop -r
    ```

### Configuration

Notia requires the following environment variables to connect to your AI model provider. You can set them as environment variables in your shell, or more conveniently, create a `.env` file in the root directory of the project.

A `.env.example` file is provided as a template. Copy it to `.env` and fill in your details:

```bash
cp .env.example .env
```

Then, populate your `.env` file with the necessary values:

```
OPENAI_API_KEY="your_api_key"
OPENAI_API_BASE="your_api_base_url"
OPENAI_API_MODEL="your_model_name" # Optional, defaults to "qwen3"
OPENAI_EMBEDDING_MODEL="your_embedding_model_name" # Optional, defaults to "nomic"
OPENAI_RERANK_MODEL="your_rerank_model_name" # Optional, defaults to "bge-reranker"
```



## Usage

Notia offers two ways to interact with your notes: a command-line interface and a web application.

### Web Interface

Notia also comes with a user-friendly web interface built with Streamlit.

To run the web application, use the following command:
```bash
streamlit run src/app.py
```
This will open a new tab in your browser with the Notia interface, where you can chat with the assistant.

### Command-Line Interface (CLI)

Once the installation and configuration are complete, you can start the application by simply running:

```bash
notia
```

You will be greeted by the `notia>` prompt. Here are a few examples of what you can do:

- **Add a new note:**
  > Add a note: I need to refactor the authentication module to use JWT. Project: auth-backend.

- **Search for notes:**
  > What are the current tasks for the backend?

- **List all your notes:**
  > List all my notes.

- **List all projects:**
  > List all projects

- **Delete a note (you need its ID from the list or add command):**
  > Delete the note with ID xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.

- **Edit a note (you need its ID from the list or add command):**
  > Edit the note with ID xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx. New content: I have refactored the authentication module. New project: auth-backend.

- **Get a note by ID:**
  > Get the note with ID xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.

- **Search for notes by project:**
  > Search for notes with project: auth-backend

- **Export notes to CSV:**
  > Export notes from project auth-backend to CSV

- **Have a conversation:**
  > Search for notes about authentication
  > [...search results...]
  > Summarize them

- **Analyze all notes:**
  > Analyze all notes.

- **Extract top keywords:**
  > Extract top keywords.
  > Extract 20 top keywords.

To exit the application, simply type `exit` or `quit`.