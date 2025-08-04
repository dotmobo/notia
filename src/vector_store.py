import chromadb
import os
from chromadb.utils import embedding_functions
import httpx # Ajout de l'import pour httpx

class VectorStore:
    def __init__(self, path: str = ".chromadb"):
        self.client = chromadb.PersistentClient(path=path)
        
        # Récupérer les variables d'environnement pour l'API OpenAI compatible
        openai_api_base = os.getenv("OPENAI_API_BASE")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_base or not openai_api_key:
            raise EnvironmentError("OPENAI_API_BASE and OPENAI_API_KEY must be set for embedding.")

        # Initialiser la fonction d'embedding OpenAI avec le modèle "nomic"
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            api_base=openai_api_base,
                        model_name=os.getenv("OPENAI_EMBEDDING_MODEL", "nomic") # Utilisation de la variable d'environnement ou "nomic" par défaut
        )

        self.collection = self.client.get_or_create_collection(
            name="notia",
            embedding_function=openai_ef
        )

    async def rerank_documents(self, query: str, documents: list[str], model: str = os.getenv("OPENAI_RERANK_MODEL", "bge-reranker")) -> list[dict]:
        """
        Reranks a list of documents based on a query using the OpenAI-compatible /rerank endpoint.
        Returns a list of dictionaries with 'index' and 'relevance_score'.
        """
        openai_api_base = os.getenv("OPENAI_API_BASE")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_base or not openai_api_key:
            print("Warning: OPENAI_API_BASE and OPENAI_API_KEY must be set for reranking. Skipping reranking.")
            return []

        rerank_url = f"{openai_api_base.rstrip('/')}/rerank"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "query": query,
            "documents": documents
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(rerank_url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status() # Lève une exception pour les réponses 4xx ou 5xx
                return response.json().get("results", [])
            except httpx.RequestError as e:
                print(f"An error occurred while requesting reranking: {e}")
                return []
            except httpx.HTTPStatusError as e:
                print(f"Error response {e.response.status_code} while requesting reranking: {e.response.text}")
                return []

    def add_note(self, note):
        self.collection.add(
            ids=[note.id],
            documents=[note.content],
            metadatas=[{"timestamp": note.timestamp.isoformat(), "tags": ",".join(note.tags)}]
        )

    def get_note(self, id: str):
        return self.collection.get(ids=[id])

    def delete_note(self, id: str):
        self.collection.delete(ids=[id])

    def search_notes(self, query: str, n_results: int = 5):
        return self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
