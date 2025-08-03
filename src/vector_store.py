import chromadb

class VectorStore:
    def __init__(self, path: str = ".chromadb"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection("notia")

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
