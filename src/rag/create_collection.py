"""Create the Qdrant collection."""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "electric_skates"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main(
    collection_name: str = COLLECTION_NAME,
    embedding_model_name: str = EMBEDDING_MODEL_NAME,
    *,
    recreate: bool = False,
) -> None:
    """Create a Qdrant collection for electric skate product chunks.

    The vector size is inferred from the SentenceTransformer model,
    so the code still works if you later switch embedding models.
    """
    qdrant_client = QdrantClient(
        host="localhost",
        port=6333,
        grpc_port=6334,
        prefer_grpc=True,
    )

    embedding_model = SentenceTransformer(embedding_model_name)
    vector_size = embedding_model.get_sentence_embedding_dimension()

    if qdrant_client.collection_exists(collection_name):
        if recreate:
            qdrant_client.delete_collection(collection_name)
        else:
            print(f"Collection '{collection_name}' already exists.")
            return

    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    print(f"Created collection '{collection_name}' with vector size {vector_size}.")


if __name__ == "__main__":
    main()
