"""
Data ingestion script for PM High Council.
Reads podcast transcripts, chunks them, and stores embeddings in ChromaDB.
"""

import re
import yaml
from pathlib import Path
from typing import Generator, List, Dict, Tuple

import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config import (
    SWARMS,
    CHROMA_DB_DIR,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
)
from persona_mapping import get_persona_for_speaker, PERSONA_MAP


def parse_transcript(file_path: Path) -> dict:
    """Parse a markdown transcript file with YAML frontmatter."""
    content = file_path.read_text(encoding="utf-8")

    # Split frontmatter from content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()
        else:
            frontmatter = {}
            body = content
    else:
        frontmatter = {}
        body = content

    return {
        "metadata": frontmatter,
        "body": body,
        "source_file": str(file_path)
    }


def clean_transcript(body: str) -> str:
    """Remove sponsor blocks and clean up transcript text."""
    lines = body.split("\n")
    cleaned_lines = []
    in_sponsor_block = False

    for line in lines:
        # Detect sponsor block start
        if "This episode is brought to you by" in line:
            in_sponsor_block = True
            continue

        # Detect sponsor block end (next speaker)
        if in_sponsor_block and re.match(r"^[A-Z][a-z]+ [A-Z]?[a-z]* ?\(\d{2}:\d{2}:\d{2}\):", line):
            in_sponsor_block = False

        if not in_sponsor_block:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def extract_speaker_segments(body: str, target_speaker: str) -> List[Dict]:
    """Extract segments where the target speaker is talking."""
    # Pattern to match speaker turns: "Speaker Name (HH:MM:SS):"
    pattern = r"^([A-Za-z][A-Za-z\- ]+) \((\d{2}:\d{2}:\d{2})\):\s*"

    segments = []
    current_speaker = None
    current_timestamp = None
    current_text = []

    def normalize(name: str) -> str:
        return name.lower().replace("-", " ").strip()

    for line in body.split("\n"):
        match = re.match(pattern, line)
        if match:
            # Save previous segment if it was from target speaker
            if current_speaker and current_text:
                speaker_norm = normalize(current_speaker)
                target_norm = normalize(target_speaker)
                if target_norm in speaker_norm or speaker_norm in target_norm:
                    segments.append({
                        "speaker": current_speaker,
                        "timestamp": current_timestamp,
                        "text": "\n".join(current_text).strip()
                    })

            # Start new segment
            current_speaker = match.group(1)
            current_timestamp = match.group(2)
            current_text = [line[match.end():]]
        else:
            # Check for mid-speech timestamp
            timestamp_match = re.match(r"^\((\d{2}:\d{2}:\d{2})\):\s*", line)
            if timestamp_match:
                current_text.append(line[timestamp_match.end():])
            else:
                current_text.append(line)

    # Don't forget last segment
    if current_speaker and current_text:
        speaker_norm = normalize(current_speaker)
        target_norm = normalize(target_speaker)
        if target_norm in speaker_norm or speaker_norm in target_norm:
            segments.append({
                "speaker": current_speaker,
                "timestamp": current_timestamp,
                "text": "\n".join(current_text).strip()
            })

    return segments


def chunk_segments(
    segments: List[Dict],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> Generator[dict, None, None]:
    """Chunk speaker segments into smaller pieces."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size * 4,  # Approximate tokens to chars
        chunk_overlap=chunk_overlap * 4,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    for segment in segments:
        if not segment["text"].strip():
            continue

        chunks = splitter.split_text(segment["text"])
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                yield {
                    "text": chunk.strip(),
                    "speaker": segment["speaker"],
                    "timestamp": segment["timestamp"],
                    "chunk_index": i
                }


def get_display_name_from_speaker(speaker_name: str) -> str:
    """Convert speaker slug to display name (e.g., 'brian-chesky' -> 'Brian Chesky')."""
    return " ".join(word.capitalize() for word in speaker_name.split("-"))


def find_all_transcripts(episodes_dir: Path) -> List[Tuple[Path, str]]:
    """
    Find all transcript files and their associated speakers.

    Returns:
        List of (transcript_path, speaker_name) tuples
    """
    transcripts = []

    if not episodes_dir.exists():
        return transcripts

    for episode_folder in episodes_dir.iterdir():
        if not episode_folder.is_dir():
            continue

        transcript_path = episode_folder / "transcript.md"
        if not transcript_path.exists():
            continue

        # Extract speaker name from folder (e.g., "elena-verna-40" -> "elena-verna")
        folder_name = episode_folder.name
        # Remove trailing numbers (episode numbers)
        speaker_name = re.sub(r'-\d+$', '', folder_name)

        transcripts.append((transcript_path, speaker_name))

    return transcripts


def ingest_transcripts():
    """Main ingestion function for the Quad-Swarm Engine."""
    print("Starting transcript ingestion for Quad-Swarm Engine...")
    print(f"Looking for transcripts in: {Path(__file__).parent.parent / 'episodes'}")

    # Initialize ChromaDB
    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(CHROMA_DB_DIR),
        settings=Settings(anonymized_telemetry=False)
    )

    # Delete existing collection if it exists
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection: {COLLECTION_NAME}")
    except Exception:
        pass  # Collection doesn't exist yet

    # Create new collection
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    print(f"Created collection: {COLLECTION_NAME}")

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY
    )

    all_documents = []
    all_metadatas = []
    all_ids = []

    # Find all transcripts
    episodes_dir = Path(__file__).parent.parent / "episodes"
    transcripts = find_all_transcripts(episodes_dir)

    print(f"\nFound {len(transcripts)} transcript files")

    # Track stats by persona
    persona_stats = {persona: 0 for persona in PERSONA_MAP.keys()}
    skipped_speakers = set()

    # Process each transcript
    for transcript_path, speaker_name in transcripts:
        # Check if speaker is in a persona swarm
        persona = get_persona_for_speaker(speaker_name)

        if persona is None:
            skipped_speakers.add(speaker_name)
            continue

        display_name = get_display_name_from_speaker(speaker_name)
        print(f"\nProcessing {display_name} ({persona})...")
        print(f"  Reading: {transcript_path}")

        # Parse transcript
        parsed = parse_transcript(transcript_path)

        # Clean transcript
        cleaned_body = clean_transcript(parsed["body"])

        # Extract speaker segments
        segments = extract_speaker_segments(cleaned_body, display_name)
        print(f"    Found {len(segments)} segments from {display_name}")

        # Chunk segments
        chunk_count = 0
        episode_folder = transcript_path.parent.name
        for chunk in chunk_segments(segments):
            doc_id = f"{speaker_name}_{episode_folder}_{chunk_count}"

            all_documents.append(chunk["text"])
            all_metadatas.append({
                "speaker_name": speaker_name,
                "persona": persona,  # NEW: swarm identifier
                "guest": display_name,
                "episode_title": parsed["metadata"].get("title", "Unknown"),
                "timestamp": chunk["timestamp"],
                "chunk_index": chunk["chunk_index"],
                "source_file": str(transcript_path)
            })
            all_ids.append(doc_id)
            chunk_count += 1

        persona_stats[persona] += chunk_count
        print(f"    Created {chunk_count} chunks")

    # Generate embeddings and add to collection
    if all_documents:
        print(f"\nGenerating embeddings for {len(all_documents)} chunks...")

        # Process in batches to avoid rate limits
        batch_size = 100
        for i in range(0, len(all_documents), batch_size):
            batch_docs = all_documents[i:i + batch_size]
            batch_metas = all_metadatas[i:i + batch_size]
            batch_ids = all_ids[i:i + batch_size]

            # Generate embeddings
            batch_embeddings = embeddings.embed_documents(batch_docs)

            # Add to collection
            collection.add(
                documents=batch_docs,
                embeddings=batch_embeddings,
                metadatas=batch_metas,
                ids=batch_ids
            )

            print(f"  Added batch {i // batch_size + 1}/{(len(all_documents) - 1) // batch_size + 1}")

    print(f"\n{'='*50}")
    print("INGESTION COMPLETE")
    print(f"{'='*50}")
    print(f"Total documents: {collection.count()}")

    # Print summary by persona swarm
    print("\nChunks by Persona Swarm:")
    for persona, display_name in [
        ("founder_swarm", "The Visionary (Founders)"),
        ("product_swarm", "The Scaler (Product)"),
        ("growth_swarm", "The Scientist (Growth)"),
        ("engineering_swarm", "The Architect (Engineering)")
    ]:
        count = persona_stats.get(persona, 0)
        print(f"  {display_name}: {count} chunks")

    # Report skipped speakers
    if skipped_speakers:
        print(f"\nSkipped speakers (not in PERSONA_MAP):")
        for speaker in sorted(skipped_speakers):
            print(f"  - {speaker}")


if __name__ == "__main__":
    ingest_transcripts()
