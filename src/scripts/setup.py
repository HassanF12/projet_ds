"""One-time setup script for RAG assistant database."""

from src.rag.create_collection import main as create_collection
from src.rag.load_embeddings import embed_and_store_files

COLLECTION_NAME = "electric_skates"

if __name__ == "__main__":
    print("Setting up database...")
    create_collection(recreate=False)
    embed_and_store_files(collection_name=COLLECTION_NAME)
