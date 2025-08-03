from agents import function_tool
from vector_store import VectorStore
from models import Note

# Initialize the vector store once
vs = VectorStore()

@function_tool
def add_note(content: str, tags: str = "") -> str:
    """
    Adds a new note with content and optional tags.
    Tags should be a comma-separated string, e.g., "bug,frontend,urgent".
    """
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    note = Note(content=content, tags=tag_list)
    vs.add_note(note)
    return f"Note added successfully with ID: {note.id}"

@function_tool
def list_all_notes() -> dict:
    """
    Lists all the notes currently stored.
    Returns a list of all notes with their content, metadata, and IDs.
    """
    # ChromaDB doesn't have a list all, so we get a large number of items.
    return vs.collection.get(limit=1000)

@function_tool
def delete_note(note_id: str) -> str:
    """
    Deletes a note specified by its unique ID.
    You must provide the exact ID of the note to delete.
    """
    vs.delete_note(note_id)
    return f"Note with ID {note_id} has been deleted."

@function_tool
def search_notes(query: str, n_results: int = 5) -> dict:
    """
    Searches for notes that are semantically similar to the given query.
    Returns a list of the top matching notes.
    """
    return vs.search_notes(query, n_results=n_results)

# Export a list of the decorated functions for the agent
tools = [add_note, list_all_notes, delete_note, search_notes]
