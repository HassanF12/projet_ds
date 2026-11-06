"""RAG customer service assistant."""

from ollama import Client
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

DEFAULT_COLLECTION_NAME = "electric_skates"
TOP_VECTOR_SEARCH = 3
# OLLAMA_MODEL = "gemma:2b"
OLLAMA_MODEL = "qwen2.5:3b"
MAX_HISTORY = 7


class RagAssistant:
    """A class to represent a RAG customer service assistant."""

    def __init__(
        self,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        top_k_vectors: int = TOP_VECTOR_SEARCH,
        model: str = OLLAMA_MODEL,
    ):
        """Initialize the assistant."""
        self.ollama_client = Client(host="http://localhost:11434")
        self.qdrant_client = QdrantClient(
            host="localhost",
            port=6333,
            grpc_port=6334,
            prefer_grpc=True,
        )
        self.embedding_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.collection_name = collection_name
        self.top_k_vectors = top_k_vectors
        self.model = model
        self.conversation_history: list[dict[str, str]] = []

    def retrieve(self, query: str) -> list[str]:
        """Retrieve the top k documents related to the given question from Qdrant."""
        embedded_query = self.embedding_model.encode(
            query,
            normalize_embeddings=True,
        ).tolist()

        query_results = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=embedded_query,
            limit=self.top_k_vectors,
            with_payload=True,
        ).points

        results = []
        for i, point in enumerate(query_results, 1):
            if point.payload is not None:
                results.append(
                    f"Option {i}:\nDate: {point.payload.get('date', 'Unknown')}\nContent:\n{point.payload.get('content', '')}"
                )
        return results

    def generate_answer(self, query: str, context_documents: list[str]) -> str:
        """Generate an answer to a question using Ollama with retrieved context."""
        if not context_documents:
            return (
                "I could not find relevant information in the electric skate documents."
            )

        context = "\n\n---\n\n".join(context_documents)

        system_instruction = """You are a helpful ans strictly factual customer service chatbot for an electric skateboard company.
Talk in the first person as you are addressing the customer directly.

IMPORTANT: Read the customer's request carefully and match it to the best board:
If they ask for a lighter board, recommend the lightest option from the context
If they ask for all-terrain, only recommend boards explicitly mentioned as "all-terrain" or "off-road capable"
If they ask for faster, recommend the fastest
If they ask for longer range, recommend the longest range
Always explain why you're recommending that specific board based on THEIR stated needs

CRITICAL: If a document says something is "NOT suitable for" or "NOT built for" what the customer asked for, DO NOT recommend it.
Examples: If the customer asks for all-terrain and the document says "Not Built for Rough Terrain", skip that board completely.

ALWAYS include the specific product name/model (e.g., "Exway Ripple", "Exway Agent") in your recommendation.
Do NOT use generic descriptions like "Lightest Option" - use the actual product name from the context.

Only recommend products that match what the customer asked for. Never recommend a product that contradicts their requirements.
"""

        history_block = ""
        if self.conversation_history:
            history_lines = []
            for msg in self.conversation_history:
                role = msg["role"].capitalize()
                content = msg["content"]
                history_lines.append(f"{role}: {content}")
            history_block = (
                "Previous conversation:\n" + "\n".join(history_lines) + "\n\n---\n\n"
            )

        prompt = f"""{system_instruction}

{history_block}Context:
{context}


Customer question:
{query}

BEFORE answering, think through this:
1. What is the customer asking for?
2. Which board from the options actually matches that requirement?
3. What specific specs make it the best choice?

Then answer the customer with the board name and specific reasons."""

        response = self.ollama_client.generate(
            model=self.model,
            prompt=prompt,
            stream=False,
        )

        return (
            response.get("response", "I could not generate an answer.")
            or "I could not generate an answer."
        )

    def query(self, query: str) -> str:
        """Query the assistant."""
        # 1. Retrieve the relevant documents from Qdrant
        context_documents = self.retrieve(query)

        # 2. Generate an answer using the retrieved documents
        answer = self.generate_answer(query, context_documents)

        # 3. Save the user's question in the conversation history
        self.conversation_history.append({"role": "user", "content": query})

        # 4. Save the assistant's answer in the conversation history
        self.conversation_history.append({"role": "assistant", "content": answer})

        # 5 & 6. Keep only the last 7 exchanges (14 messages)
        max_exchanges = 7
        self.conversation_history = self.conversation_history[-(max_exchanges * 2) :]

        # 7. Return the generated answer
        return answer
