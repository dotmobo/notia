import logging
from agents import function_tool
from models import Note
from rich.table import Table
from console import console
from vector_store import vs

LOG = logging.getLogger(__name__)


@function_tool
def add_note(content: str, project: str = "") -> str:
    """
    Adds a new note with content and optional project.

    Args:
        content (str): The main content of the note.
        project (str, optional): The project name for this note. Defaults to "".

    Returns:
        str: A confirmation message with the new note's ID.
    """
    LOG.info("Tool called: add_note")
    note = Note(content=content, project=project)
    vs.add_note(note)
    return f"Note added successfully with ID: {note.id}"


@function_tool
def list_all_notes() -> dict:
    """
    Lists all notes, displaying them to the user in a formatted table and returning the raw data.
    The user has already seen the formatted table in the console.

    Returns:
        dict: The raw data of all notes from the vector store.
    """
    LOG.info("Tool called: list_all_notes")

    notes_data = vs.get_all_notes()

    if not notes_data or not notes_data.get("ids"):
        console.print("[bold yellow]No notes found.[/bold yellow]")
        return {}

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=36)
    table.add_column("Content")
    table.add_column("Project")
    table.add_column("Timestamp")

    for i, note_id in enumerate(notes_data["ids"]):
        content = notes_data["documents"][i]
        metadata = notes_data["metadatas"][i]
        project = metadata.get("project", "")
        timestamp = metadata.get("timestamp", "")

        table.add_row(note_id, content, project, timestamp)

    console.print(table)

    return notes_data


@function_tool
def delete_note(note_id: str) -> str:
    """
    Deletes a note specified by its unique ID.

    Args:
        note_id (str): The exact ID of the note to be deleted.

    Returns:
        str: A confirmation message indicating the note has been deleted.
    """
    LOG.info(f"Tool called: delete_note with id: {note_id}")
    vs.delete_note(note_id)
    return f"Note with ID {note_id} has been deleted."


@function_tool
def edit_note(note_id: str, new_content: str, new_project: str = "") -> str:
    """
    Overwrites an existing note with new content and project.

    This function completely replaces the content and project of an existing note
    identified by its ID. The timestamp is automatically updated to the current time.

    Args:
        note_id (str): The ID of the note to edit.
        new_content (str): The new content to overwrite the note with.
        new_project (str, optional): The new project name. Defaults to "".

    Returns:
        str: A confirmation message indicating the note has been updated.
    """
    LOG.info(f"Tool called: edit_note with id: {note_id}")

    # Create a new note object with the provided data
    note = Note(
        content=new_content,
        project=new_project,
        id=note_id,
    )
    vs.update_note(note)
    return f"Note with ID {note_id} has been updated."


@function_tool
def get_note_by_id(note_id: str) -> dict:
    """
    Retrieves and displays a single note by its ID.

    Args:
        note_id (str): The exact ID of the note to retrieve.

    Returns:
        dict: The raw data of the note from the vector store.
    """
    LOG.info(f"Tool called: get_note_by_id with id: {note_id}")

    note_data = vs.get_note(note_id)

    if not note_data or not note_data.get("ids"):
        console.print(f"[bold yellow]No note found with ID: {note_id}[/bold yellow]")
        return {}

    table = Table(show_header=True, header_style="bold green")
    table.add_column("ID", style="dim", width=36)
    table.add_column("Content")
    table.add_column("Project")
    table.add_column("Timestamp")

    content = note_data["documents"][0]
    metadata = note_data["metadatas"][0]
    project = metadata.get("project", "")
    timestamp = metadata.get("timestamp", "")

    table.add_row(note_id, content, project, timestamp)

    console.print(table)

    return note_data


@function_tool
def search_notes_by_project(project: str) -> dict:
    """
    Searches for notes by project and displays them to the user.

    Args:
        project (str): The project name to search for.

    Returns:
        dict: The raw search result data from the vector store.
    """
    LOG.info(f"Tool called: search_notes_by_project with project: '{project}'")

    notes_data = vs.get_notes_by_project(project)

    if not notes_data or not notes_data.get("ids"):
        console.print("[bold yellow]No matching notes found.[/bold yellow]")
        return {}

    table = Table(
        title=f"Search Results for project: '{project}'",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("ID", style="dim", width=36)
    table.add_column("Content")
    table.add_column("Project")
    table.add_column("Timestamp")

    for i, note_id in enumerate(notes_data["ids"]):
        content = notes_data["documents"][i]
        metadata = notes_data["metadatas"][i]
        project = metadata.get("project", "")
        timestamp = metadata.get("timestamp", "")

        table.add_row(note_id, content, project, timestamp)

    console.print(table)

    return notes_data


@function_tool
def list_all_projects() -> list[str]:
    """
    Lists all unique projects in the system.

    Returns:
        list[str]: List of all unique project names.
    """
    LOG.info("Tool called: list_all_projects")

    projects = vs.get_all_projects()

    if not projects:
        console.print("[bold yellow]No projects found.[/bold yellow]")
        return []

    console.print(f"[bold green]Found {len(projects)} project(s):[/bold green]")
    for i, project in enumerate(projects, 1):
        console.print(f"  {i}. {project}")

    return projects


@function_tool
async def search_notes(
    query: str, initial_n_results: int = 20, final_n_results: int = 5
) -> dict:
    """
    Searches for notes, displays them to the user in a formatted table, and returns the raw data.
    The user has already seen the formatted table in the console.

    Args:
        query (str): The search query for finding semantically similar notes.
        initial_n_results (int, optional): The number of results to retrieve from the vector store before reranking. Defaults to 20.
        final_n_results (int, optional): The number of top results to return after reranking. Defaults to 5.

    Returns:
        dict: The raw search result data from the vector store.
    """
    LOG.info(f"Tool called: search_notes with query: '{query}'")

    search_results = vs.search_notes(query, n_results=initial_n_results)

    if (
        not search_results
        or not search_results.get("ids")
        or not search_results["ids"][0]
    ):
        console.print("[bold yellow]No matching notes found.[/bold yellow]")
        return {}

    ids = search_results["ids"][0]
    documents = search_results["documents"][0]
    metadatas = search_results["metadatas"][0]
    distances = search_results["distances"][0]

    # Rerank the results using the rerank_documents method
    reranked_results = await vs.rerank_documents(query, documents)
    rerank_scores = {doc["index"]: doc["relevance_score"] for doc in reranked_results}

    combined_results = []
    for i, note_id in enumerate(ids):
        combined_results.append(
            {
                "id": note_id,
                "content": documents[i],
                "project": metadatas[i].get("project", ""),
                "timestamp": metadatas[i].get("timestamp", ""),
                "distance": distances[i],
                "rerank_score": rerank_scores.get(i, 0.0),
            }
        )
    # Sort the combined results by rerank score and take the top final_n_results
    combined_results.sort(key=lambda x: x["rerank_score"], reverse=True)
    final_results = combined_results[:final_n_results]

    table = Table(
        title=f"Search Results for: '{query}'",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("ID", style="dim", width=36)
    table.add_column("Content")
    table.add_column("Project")
    table.add_column("Timestamp")
    table.add_column("Distance", style="yellow")
    table.add_column("Rerank Score", style="green")

    for result in final_results:
        table.add_row(
            result["id"],
            result["content"],
            result["project"],
            result["timestamp"],
            f"{result['distance']:.4f}",
            f"{result['rerank_score']:.4f}",
        )

    console.print(table)

    return {
        "ids": [[r["id"] for r in final_results]],
        "documents": [[r["content"] for r in final_results]],
        "metadatas": [
            [
                {
                    "project": r["project"],
                    "timestamp": r["timestamp"],
                    "rerank_score": r["rerank_score"],
                }
                for r in final_results
            ]
        ],
        "distances": [[r["distance"] for r in final_results]],
    }


# Export a list of the decorated functions for the agent
tools = [
    add_note,
    list_all_notes,
    delete_note,
    search_notes,
    edit_note,
    get_note_by_id,
    search_notes_by_project,
    list_all_projects,
]
