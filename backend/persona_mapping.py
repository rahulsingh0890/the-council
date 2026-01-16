"""
Persona Mapping for the Quad-Swarm Engine

Maps individual speakers to their respective persona swarms.
"""

from typing import Optional, List

PERSONA_MAP = {
    "founder_swarm": [
        "brian-chesky", "tobi-lutke", "marc-benioff", "dylan-field",
        "stewart-butterfield", "ben-horowitz", "nikita-bier", "kunal-shah"
    ],
    "product_swarm": [
        "marty-cagan", "shreyas-doshi", "julie-zhuo", "gibson-biddle",
        "tomer-cohen", "noam-lovinsky", "lenny-rachitsky"
    ],
    "growth_swarm": [
        "elena-verna", "brian-balfour", "casey-winters", "sean-ellis",
        "ayo-omojola", "sri-batchu", "patrick-campbell"
    ],
    "engineering_swarm": [
        "will-larson", "camille-fournier", "david-singleton", "farhan-thawar",
        "dhanji-r-prasanna", "chip-huyen", "geoff-charles"
    ]
}


def get_persona_for_speaker(speaker_name: str) -> Optional[str]:
    """
    Returns the swarm persona for a given speaker, or None if not mapped.

    Args:
        speaker_name: The speaker identifier (e.g., "brian-chesky")

    Returns:
        The persona swarm name (e.g., "founder_swarm") or None if not found
    """
    for persona, speakers in PERSONA_MAP.items():
        if speaker_name in speakers:
            return persona
    return None


def get_all_speakers() -> List[str]:
    """Returns a flat list of all mapped speakers across all swarms."""
    return [speaker for speakers in PERSONA_MAP.values() for speaker in speakers]


def get_speakers_for_persona(persona: str) -> List[str]:
    """
    Returns the list of speakers for a given persona swarm.

    Args:
        persona: The persona swarm name (e.g., "founder_swarm")

    Returns:
        List of speaker identifiers, or empty list if persona not found
    """
    return PERSONA_MAP.get(persona, [])
