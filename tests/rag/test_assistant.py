"""Unit tests for run_assistant script."""

from unittest.mock import patch


def test_quit_exits_the_assistant() -> None:
    with (
        patch("src.rag.assistant.Client"),
        patch("src.rag.assistant.QdrantClient"),
        patch("src.rag.assistant.SentenceTransformer"),
        patch("builtins.input", return_value="q"),
        patch("builtins.print") as mock_print,
    ):
        from src.scripts.run_assistant import main

        main()

        mock_print.assert_any_call("\nGoodbye!")
