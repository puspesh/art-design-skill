"""
Engine registry for image generation.

Provides factory function to get engine instances by name.
"""

from typing import Union

from typing import Optional

from .base import BaseEngine, GenerationRequest, GenerationResult
from .gemini import GeminiNanoBananaProEngine
from .midjourney import MidjourneyEngine
from .nano_banana_pro import NanoBananaProEngine

# Engine aliases mapping
ENGINE_ALIASES = {
    "midjourney": "midjourney",
    "mj": "midjourney",
    "nano-banana-pro": "nano-banana-pro",
    "nbp": "nano-banana-pro",
    "gemini": "gemini-nano-banana-pro",
}

# Engine class mapping
ENGINE_CLASSES = {
    "midjourney": MidjourneyEngine,
    "nano-banana-pro": NanoBananaProEngine,
    "gemini-nano-banana-pro": GeminiNanoBananaProEngine,
}


def get_engine(
    name: str, api_key: str, gemini_api_key: Optional[str] = None
) -> BaseEngine:
    """
    Get an engine instance by name.

    For 'nbp' / 'nano-banana-pro': prefers Gemini API if gemini_api_key is
    provided, otherwise falls back to APIframe.

    Args:
        name: Engine name or alias
        api_key: APIframe API key
        gemini_api_key: Google Gemini API key (optional)

    Returns:
        Engine instance

    Raises:
        ValueError: If engine name is unknown or required key is missing
    """
    # Resolve alias
    canonical_name = ENGINE_ALIASES.get(name.lower())
    if canonical_name is None:
        valid = ", ".join(ENGINE_ALIASES.keys())
        raise ValueError(f"Unknown engine '{name}'. Valid engines: {valid}")

    # Smart routing: nbp prefers Gemini when key is available
    if canonical_name == "nano-banana-pro" and gemini_api_key:
        print("  (using Gemini API — GEMINI_API_KEY detected)")
        return GeminiNanoBananaProEngine(gemini_api_key)

    # Explicit gemini requires its own key
    if canonical_name == "gemini-nano-banana-pro":
        if not gemini_api_key:
            raise ValueError(
                "Engine 'gemini' requires GEMINI_API_KEY. "
                "Set it in your environment or .env file."
            )
        return GeminiNanoBananaProEngine(gemini_api_key)

    # Default: use APIframe-backed engine
    engine_class = ENGINE_CLASSES.get(canonical_name)
    if engine_class is None:
        raise ValueError(f"Engine '{canonical_name}' not implemented")

    return engine_class(api_key)


def list_engines() -> list[str]:
    """Return list of available engine names."""
    return list(ENGINE_CLASSES.keys())


__all__ = [
    "BaseEngine",
    "GenerationRequest",
    "GenerationResult",
    "GeminiNanoBananaProEngine",
    "MidjourneyEngine",
    "NanoBananaProEngine",
    "get_engine",
    "list_engines",
    "ENGINE_ALIASES",
]
