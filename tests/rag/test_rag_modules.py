"""Unit tests for the RAG modules."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.rag.assistant import RagAssistant
from src.rag.create_collection import main as create_collection
from src.rag.load_embeddings import (
    embed_and_store_files,
    embed_txt_file,
    insert_into_qdrant,
)


@pytest.fixture
def assistant() -> RagAssistant:
    with (
        patch("src.rag.assistant.Client"),
        patch("src.rag.assistant.QdrantClient"),
        patch("src.rag.assistant.SentenceTransformer"),
    ):
        return RagAssistant()


def test_retrieve_formats_documents(assistant: RagAssistant) -> None:
    point = MagicMock(payload={"date": "2024-01-01", "content": "Fast board"})
    empty = MagicMock(payload=None)
    assistant.qdrant_client.query_points.return_value.points = [point, empty]

    assert assistant.retrieve("fast?") == [
        "Option 1:\nDate: 2024-01-01\nContent:\nFast board"
    ]


def test_generate_answer_without_context(assistant: RagAssistant) -> None:
    assert "could not find" in assistant.generate_answer("q", [])


def test_generate_answer_uses_history_and_ollama(assistant: RagAssistant) -> None:
    assistant.conversation_history = [{"role": "user", "content": "hi"}]
    assistant.ollama_client.generate.return_value = {"response": "Exway Ripple"}

    assert assistant.generate_answer("q", ["doc"]) == "Exway Ripple"
    prompt = assistant.ollama_client.generate.call_args.kwargs["prompt"]
    assert "User: hi" in prompt


def test_generate_answer_empty_response(assistant: RagAssistant) -> None:
    assistant.ollama_client.generate.return_value = {"response": ""}

    assert "could not generate" in assistant.generate_answer("q", ["doc"])


def test_query_keeps_bounded_history(assistant: RagAssistant) -> None:
    with (
        patch.object(assistant, "retrieve", return_value=["doc"]),
        patch.object(assistant, "generate_answer", return_value="answer"),
    ):
        for _ in range(10):
            assert assistant.query("q") == "answer"

    assert len(assistant.conversation_history) == 14


def test_embed_txt_file(tmp_path: Path) -> None:
    file = tmp_path / "a.txt"
    file.write_text("2024-01-01\nSome content\n", encoding="utf-8")
    model = MagicMock()
    model.encode.return_value.tolist.return_value = [0.1, 0.2]

    assert embed_txt_file(file, model) == {
        "content": "Some content",
        "date": "2024-01-01",
        "embedding": [0.1, 0.2],
    }


def test_insert_into_qdrant() -> None:
    client = MagicMock()
    insert_into_qdrant(client, "c", [{"content": "x", "date": "d", "embedding": [0.1]}])

    client.upsert.assert_called_once()


def test_embed_and_store_files(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("2024\ncontent", encoding="utf-8")
    model = MagicMock()
    model.encode.return_value.tolist.return_value = [0.1]

    with patch("src.rag.load_embeddings.QdrantClient") as client:
        embed_and_store_files("c", str(tmp_path), model)

    client.return_value.upsert.assert_called_once()


def test_embed_and_store_files_no_files(tmp_path: Path) -> None:
    with (
        patch("src.rag.load_embeddings.QdrantClient"),
        pytest.raises(FileNotFoundError),
    ):
        embed_and_store_files("c", str(tmp_path), MagicMock())


@pytest.mark.parametrize(
    ("exists", "recreate", "created"),
    [(False, False, True), (True, False, False), (True, True, True)],
)
def test_create_collection(*, exists: bool, recreate: bool, created: bool) -> None:
    with (
        patch("src.rag.create_collection.QdrantClient") as client,
        patch("src.rag.create_collection.SentenceTransformer") as model,
    ):
        model.return_value.get_sentence_embedding_dimension.return_value = 384
        client.return_value.collection_exists.return_value = exists

        create_collection(recreate=recreate)

    assert client.return_value.create_collection.called is created
