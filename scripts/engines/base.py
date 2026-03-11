"""
Base engine abstraction for image generation.

Provides abstract base class and data classes for multi-engine support.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GenerationRequest:
    """Unified request format for all engines."""

    prompt: str
    aspect_ratio: str = "1:1"
    resolution: Optional[str] = None  # For Nano Banana Pro (1K, 2K, 4K)
    input_images: list[str] = field(default_factory=list)  # URLs or base64 for editing

    # Midjourney-specific reference parameters
    style_reference: Optional[str] = None
    style_weight: int = 100
    character_reference: Optional[str] = None
    character_weight: int = 100
    image_prompt: Optional[str] = None
    image_weight: float = 1.0

    # Auto brand reference fields (separate from user-provided refs)
    brand_references: list[str] = field(default_factory=list)  # Local paths for multimodal engines
    brand_sref: Optional[str] = None  # Midjourney --sref URL from config
    brand_sref_weight: int = 100  # Midjourney --sw from config
    brand_style_instruction: str = ""  # Text instruction prepended for multimodal engines


@dataclass
class GenerationResult:
    """Unified result format from all engines."""

    task_id: str
    status: str
    image_urls: list[str] = field(default_factory=list)
    percentage: str = "0"
    raw_response: dict = field(default_factory=dict)


class BaseEngine(ABC):
    """Abstract base class for image generation engines."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Engine identifier."""
        pass

    @property
    @abstractmethod
    def supports_editing(self) -> bool:
        """Whether engine supports image editing."""
        pass

    @abstractmethod
    def submit(self, request: GenerationRequest) -> str:
        """
        Submit generation request.

        Args:
            request: Generation request with prompt and parameters

        Returns:
            task_id for polling
        """
        pass

    @abstractmethod
    def fetch(self, task_id: str) -> GenerationResult:
        """
        Fetch result for a task.

        Args:
            task_id: Task ID from submit()

        Returns:
            GenerationResult with status and image URLs
        """
        pass

    @abstractmethod
    def build_prompt(self, request: GenerationRequest) -> str:
        """
        Build engine-specific prompt from request.

        Args:
            request: Generation request

        Returns:
            Engine-formatted prompt string
        """
        pass
