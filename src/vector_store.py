import chromadb
import os
from chromadb.utils import embedding_functions
import httpx
import logging

from models import Note

LOG = logging.getLogger(__name__)


class VectorStore:
    """
    Vector store for managing document embeddings.
    This class initializes a persistent ChromaDB client and provides methods
    to add, retrieve, delete, and search notes.
    It uses OpenAI-compatible embedding functions for document embeddings.
    Attributes:
        client (chromadb.PersistentClient): The ChromaDB client instance.
        collection (chromadb.Collection): The collection for storing notes.
        openai_api_base (str): Base URL for OpenAI API.
        openai_api_key (str): API key for OpenAI.
        openai_embedding_model (str): Model name for OpenAI embeddings.
        openai_rerank_model (str): Model name for OpenAI reranking.
    Methods:
        rerank_documents(query, documents, model): Reranks documents based on a query.
        add_note(note): Adds a note to the vector store.
        get_note(id): Retrieves a note by its ID.
        delete_note(id): Deletes a note by its ID.
        search_notes(query, n_results): Searches for notes based on a query.
    """

    def __init__(self, path: str = ".chromadb"):
        self.openai_api_base = os.getenv("OPENAI_API_BASE")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "nomic")
        self.openai_rerank_model = os.getenv("OPENAI_RERANK_MODEL", "bge-reranker")
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(
            name="notia",
            embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                api_key=self.openai_api_key,
                api_base=self.openai_api_base,
                model_name=self.openai_embedding_model,
            ),
        )

    async def rerank_documents(
        self,
        query: str,
        documents: list[str],
    ) -> list[dict]:
        """
        Reranks documents based on a query using OpenAI's reranking model.

        Args:
            query (str): The search query for reranking.
            documents (list[str]): List of documents to be reranked.

        Returns:
            list[dict]: List of reranked documents with scores.
        """

        rerank_url = f"{self.openai_api_base.rstrip('/')}/rerank"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.openai_rerank_model,
            "query": query,
            "documents": documents,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    rerank_url, headers=headers, json=payload, timeout=30.0
                )
                response.raise_for_status()
                return response.json().get("results", [])
            except httpx.RequestError as e:
                LOG.error(f"Request error during reranking: {e}")
                return []
            except httpx.HTTPStatusError as e:
                LOG.error(
                    f"Error response {e.response.status_code} while requesting reranking: {e.response.text}"
                )
                return []

    def add_note(self, note: Note):
        """
        Adds a note to the vector store.

        Args:
            note (Note): The note object to be added.
        Returns:
            None
        """
        LOG.info(f"Adding note with ID {note.id} to vector store.")
        self.collection.add(
            ids=[note.id],
            documents=[note.content],
            metadatas=[
                {"timestamp": note.timestamp.isoformat(), "project": note.project or ""}
            ],
        )

    def get_note(self, id: str) -> chromadb.GetResult:
        """
        Retrieves a note by its ID.

        Args:
            id (str): The unique identifier of the note.

        Returns:
            chromadb.GetResult: The note data retrieved from the vector store.
        """
        LOG.info(f"Retrieving note with ID {id} from vector store.")
        return self.collection.get(ids=[id])

    def update_note(self, note: Note):
        """
        Overwrites an existing note in the vector store.

        If a note with the same ID already exists, its content, project, and timestamp
        will be completely replaced with the new data provided in the `note` object.

        Args:
            note (Note): The note object containing the new data.
        Returns:
            None
        """
        LOG.info(f"Updating note with ID {note.id} in vector store.")
        self.collection.update(
            ids=[note.id],
            documents=[note.content],
            metadatas=[
                {"timestamp": note.timestamp.isoformat(), "project": note.project or ""}
            ],
        )

    def delete_note(self, id: str):
        """
        Deletes a note by its ID.

        Args:
            id (str): The unique identifier of the note to be deleted.

        Returns:
            None
        """
        LOG.info(f"Deleting note with ID {id} from vector store.")
        self.collection.delete(ids=[id])

    def search_notes(self, query: str, n_results: int = 5) -> chromadb.QueryResult:
        """
        Searches for notes based on a query.

        Args:
            query (str): The search query.
            n_results (int): The number of results to return.

        Returns:
            chromadb.QueryResult: The search results containing note IDs, documents, and metadata.
        """
        LOG.info(f"Searching notes with query: '{query}'")
        return self.collection.query(query_texts=[query], n_results=n_results)

    def get_all_notes(self) -> chromadb.QueryResult:
        """
        Retrieves all notes from the vector store.

        Returns:
            chromadb.QueryResult: All notes in the database.
        """
        LOG.info("Retrieving all notes from vector store.")
        return self.collection.get(limit=1000)

    def get_notes_by_project(self, project: str) -> dict:
        """
        Retrieves notes that belong to the specified project using ChromaDB metadata query.

        Args:
            project (str): The project name to search for.

        Returns:
            dict: The search results containing note IDs, documents, and metadata.
        """
        LOG.info(f"Retrieving notes with project: {project}")
        
        # Use ChromaDB's where clause to filter by metadata
        results = self.collection.get(
            where={"project": project},
            limit=1000
        )
        
        return results


# Initialize the vector store once
vs = VectorStore()
