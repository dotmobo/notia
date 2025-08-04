import chromadb
import os
from chromadb.utils import embedding_functions

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
