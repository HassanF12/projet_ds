import uuid
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "electric_skates"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DATA_DIR = "data"


def embed_txt_file(
    file_path: str | Path,
    embedding_model: SentenceTransformer | None = None,
) -> dict[str, Any]:
    """Load one short markdown file and create one embedding for the whole file."""
    if not embedding_model:
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    file_path = Path(file_path)
    lines = file_path.read_text(encoding="utf-8").strip().splitlines()
    document_date = lines[0]
    content = "\n".join(lines[1:]).strip()

    embedding = embedding_model.encode(
        content,
        normalize_embeddings=True,
    ).tolist()

    return {
        "content": content,
        "date": document_date,
        "embedding": embedding,
    }


def insert_into_qdrant(
    qdrant_client: QdrantClient,
    collection_name: str,
    documents: list[dict[str, Any]],
) -> None:
    """Save one point per markdown file into Qdrant."""
    points = []

    for document in documents:
        payload = {
            "content": document["content"],
            "date": document["date"],
        }

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=document["embedding"],
                payload=payload,
            )
        )

    qdrant_client.upsert(
        collection_name=collection_name,
        points=points,
    )


def embed_and_store_files(
    collection_name: str = COLLECTION_NAME,
    data_dir: str = DATA_DIR,
    embedding_model: SentenceTransformer | None = None,
) -> None:
    """Load all .txt files from data_dir and store them in Qdrant."""
    qdrant_client = QdrantClient(
        host="localhost",
        port=6333,
        grpc_port=6334,
        prefer_grpc=True,
    )

    txt_files = sorted(Path(data_dir).glob("*.txt"))

    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in {data_dir}/")

    documents = []

    for file_path in txt_files:
        print(f"Loading {file_path}...")
        document = embed_txt_file(file_path, embedding_model)
        documents.append(document)

    insert_into_qdrant(
        qdrant_client=qdrant_client,
        collection_name=collection_name,
        documents=documents,
    )

    print(f"Saved {len(documents)} files to Qdrant.")


if __name__ == "__main__":
    embed_and_store_files()
