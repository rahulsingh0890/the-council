"""
Base RAG agent for PM High Council swarms.
"""

from typing import Callable

import chromadb
from chromadb.config import Settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import (
    CHROMA_DB_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    LLM_MODEL,
    OPENAI_API_KEY,
)


def create_swarm_agent(
    persona_type: str,
    system_prompt: str,
    display_name: str
) -> Callable[[str], dict]:
    """
    Create a RAG-enabled swarm agent that retrieves context from a collective of speakers.

    Args:
        persona_type: The swarm identifier for filtering (e.g., "founder_swarm")
        system_prompt: The collective persona system prompt
        display_name: Human-readable name for the swarm (e.g., "The Visionary")

    Returns:
        A callable that takes a query and returns a response with sources
    """

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path=str(CHROMA_DB_DIR),
        settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_collection(COLLECTION_NAME)

    # Initialize embeddings and LLM
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY
    )

    llm = ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=OPENAI_API_KEY,
        temperature=0.7
    )

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt + "\n\n---\n\nRelevant wisdom from the collective:\n{context}"),
        ("human", "{query}")
    ])

    # Create chain
    chain = prompt | llm | StrOutputParser()

    def invoke(query: str) -> dict:
        """
        Invoke the swarm agent with a query.

        Args:
            query: The user's question

        Returns:
            Dict with 'response', 'sources', and 'agent' keys
        """
        # Generate query embedding
        query_embedding = embeddings.embed_query(query)

        # Retrieve relevant chunks filtered by persona swarm
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=8,  # Increased to get diverse perspectives from swarm
            where={"persona": persona_type},
            include=["documents", "metadatas"]
        )

        # Format context with attribution to individual speakers
        context_parts = []
        sources = []

        if results["documents"] and results["documents"][0]:
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                speaker_name = meta.get("speaker_name", "Unknown")
                display_speaker = " ".join(word.capitalize() for word in speaker_name.split("-"))
                timestamp = meta.get("timestamp", "N/A")

                context_parts.append(f"[{display_speaker} - {timestamp}] {doc}")
                sources.append({
                    "text": doc[:200] + "..." if len(doc) > 200 else doc,
                    "speaker": display_speaker,
                    "episode": meta.get("episode_title", "Unknown"),
                    "timestamp": timestamp
                })

        context = "\n\n".join(context_parts) if context_parts else "No relevant context found from this collective."

        # Generate response
        response = chain.invoke({
            "context": context,
            "query": query
        })

        return {
            "response": response,
            "sources": sources,
            "agent": display_name
        }

    return invoke


# Keep backwards compatibility alias (deprecated)
def create_rag_agent(speaker_name: str, system_prompt: str, display_name: str) -> Callable[[str], dict]:
    """
    DEPRECATED: Use create_swarm_agent instead.
    This function is kept for backwards compatibility only.
    """
    return create_swarm_agent(
        persona_type=speaker_name,  # Assumes speaker_name is now persona_type
        system_prompt=system_prompt,
        display_name=display_name
    )
