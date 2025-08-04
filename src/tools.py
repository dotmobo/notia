import logging
from agents import function_tool
from vector_store import VectorStore
from models import Note
from rich.console import Console
from rich.table import Table

LOG = logging.getLogger(__name__)

# Initialize the vector store once
vs = VectorStore()

@function_tool
def add_note(content: str, tags: str = "") -> str:
    """Adds a new note with content and optional tags.

    Args:
        content (str): The main content of the note.
        tags (str, optional): A comma-separated string of tags. Defaults to "".

    Returns:
        str: A confirmation message with the new note's ID.
    """
    LOG.info(f"Tool called: add_note")
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    note = Note(content=content, tags=tag_list)
    vs.add_note(note)
    return f"Note added successfully with ID: {note.id}"

@function_tool
def list_all_notes() -> dict:
    """Lists all notes, displaying them to the user in a formatted table and returning the raw data.
    The user has already seen the formatted table in the console.

    Returns:
        dict: The raw data of all notes from the vector store.
    """
    LOG.info("Tool called: list_all_notes")
    
    notes_data = vs.collection.get(limit=1000)
    
    if not notes_data or not notes_data.get('ids'):
        print("No notes found.")
        return {}

    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=36)
    table.add_column("Content")
    table.add_column("Tags")
    table.add_column("Timestamp")

    for i, note_id in enumerate(notes_data['ids']):
        content = notes_data['documents'][i]
        metadata = notes_data['metadatas'][i]
        tags = metadata.get('tags', '')
        timestamp = metadata.get('timestamp', '')
        
        table.add_row(
            note_id,
            content,
            tags,
            timestamp
        )

    console.print(table)
    
    return notes_data

@function_tool
def delete_note(note_id: str) -> str:
    """Deletes a note specified by its unique ID.

    Args:
        note_id (str): The exact ID of the note to be deleted.

    Returns:
        str: A confirmation message indicating the note has been deleted.
    """
    LOG.info(f"Tool called: delete_note with id: {note_id}")
    vs.delete_note(note_id)
    return f"Note with ID {note_id} has been deleted."

@function_tool
def search_notes(query: str, n_results: int = 5) -> dict:
    """Searches for notes, displays them to the user in a formatted table, and returns the raw data.
    The user has already seen the formatted table in the console.

    Args:
        query (str): The search query for finding semantically similar notes.
        n_results (int, optional): The number of results to return. Defaults to 5.

    Returns:
        dict: The raw search result data from the vector store.
    """
    LOG.info(f"Tool called: search_notes with query: '{query}'")
    
    search_results = vs.search_notes(query, n_results=n_results)
    
    if not search_results or not search_results.get('ids') or not search_results['ids'][0]:
        print("No matching notes found.")
        return {}

    console = Console()
    table = Table(title=f"Search Results for: '{query}'", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=36)
    table.add_column("Content")
    table.add_column("Tags")
    table.add_column("Timestamp")
    table.add_column("Distance", style="yellow")

    ids = search_results['ids'][0]
    documents = search_results['documents'][0]
    metadatas = search_results['metadatas'][0]
    distances = search_results['distances'][0]

    for i, note_id in enumerate(ids):
        content = documents[i]
        metadata = metadatas[i]
        distance = distances[i]
        
        tags = metadata.get('tags', '')
        timestamp = metadata.get('timestamp', '')
        
        table.add_row(
            note_id,
            content,
            tags,
            timestamp,
            f"{distance:.4f}"
        )

    console.print(table)
    
    return search_results

# Export a list of the decorated functions for the agent
tools = [add_note, list_all_notes, delete_note, search_notes]