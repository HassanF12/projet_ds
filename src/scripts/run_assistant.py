"""Main script to run the RAG assistant for electric skateboard customer support."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag.assistant import RagAssistant


def main() -> None:
    """Run the RAG assistant in interactive mode."""
    print("Initializing RAG Assistant...")
    assistant = RagAssistant()

    print("RAG Assistant ready! Type 'quit', 'exit' or 'q' to exit.\n")

    while True:
        try:
            user_input = input("Customer: ").strip()

            if user_input.lower() in ("quit", "exit", "q"):
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            print("\nFetching answer...\n")
            answer = assistant.query(user_input)
            print(f"Assistant:\n{answer}\n")
            print("-" * 50 + "\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break

        except Exception as e:
            print(f"\nAn error occurred: {e}\n")


if __name__ == "__main__":
    main()
