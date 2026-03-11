"""
Nano Banana Pro (Gemini image model) engine via APIframe.

Supports both image generation and editing.
"""

import base64
import re
from pathlib import Path

import requests

from .base import BaseEngine, GenerationRequest, GenerationResult


class NanoBananaProEngine(BaseEngine):
    """Nano Banana Pro image generation/editing engine via APIframe."""

    ENDPOINT = "https://api.apiframe.pro/nano-banana-pro"
    FETCH_ENDPOINT = "https://api.apiframe.pro/fetch"

    def __init__(self, api_key: str):
        """
        Initialize Nano Banana Pro engine.

        Args:
            api_key: APIframe API key
        """
        self.api_key = api_key
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": api_key,
        }

    @property
    def name(self) -> str:
        return "nano-banana-pro"

    @property
    def supports_editing(self) -> bool:
        return True

    def submit(self, request: GenerationRequest) -> str:
        """Submit generation/editing request to Nano Banana Pro."""
        prompt = self.build_prompt(request)

        payload = {
            "prompt": prompt,
        }

        # Add aspect ratio if provided
        if request.aspect_ratio:
            payload["aspect_ratio"] = request.aspect_ratio

        # Add resolution if specified (1K, 2K, 4K)
        if request.resolution:
            payload["resolution"] = request.resolution

        # Add input images for editing
        if request.input_images:
            payload["images"] = self._prepare_images(request.input_images)
        elif request.brand_references:
            # Use brand reference images for style anchoring
            payload["images"] = self._prepare_images(request.brand_references)
            if request.brand_style_instruction:
                payload["prompt"] = f"{request.brand_style_instruction} {payload['prompt']}"

        response = requests.post(
            self.ENDPOINT, headers=self._headers, json=payload
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"API error {response.status_code}: {response.text}"
            )

        data = response.json()
        task_id = data.get("task_id")

        if not task_id:
            raise RuntimeError(f"No task_id in response: {data}")

        return task_id

    def fetch(self, task_id: str) -> GenerationResult:
        """Fetch result for a Nano Banana Pro task."""
        payload = {"task_id": task_id}

        response = requests.post(
            self.FETCH_ENDPOINT, headers=self._headers, json=payload
        )

        if response.status_code != 200:
            return GenerationResult(
                task_id=task_id,
                status="error",
                raw_response={"message": response.text},
            )

        data = response.json()

        # Extract image URLs
        image_urls = data.get("image_urls", [])
        if not image_urls:
            single_url = data.get("original_image_url")
            if single_url:
                image_urls = [single_url]

        return GenerationResult(
            task_id=task_id,
            status=data.get("status", "unknown"),
            image_urls=image_urls,
            percentage=data.get("percentage", "0"),
            raw_response=data,
        )

    def build_prompt(self, request: GenerationRequest) -> str:
        """
        Build prompt for Nano Banana Pro.

        Strips Midjourney-specific flags since NBP doesn't use them.
        """
        prompt = request.prompt.strip().replace("\n", " ")

        # Remove Midjourney-specific flags
        prompt = re.sub(r"--style\s+\w+", "", prompt)
        prompt = re.sub(r"--no\s+[\w\s]+(?=--|$)", "", prompt)
        prompt = re.sub(r"--v\s+[\d.]+", "", prompt)
        prompt = re.sub(r"--ar\s+[\d:.]+", "", prompt)  # AR handled separately
        prompt = re.sub(r"--sref\s+\S+", "", prompt)
        prompt = re.sub(r"--sw\s+\d+", "", prompt)
        prompt = re.sub(r"--cref\s+\S+", "", prompt)
        prompt = re.sub(r"--cw\s+\d+", "", prompt)
        prompt = re.sub(r"--iw\s+[\d.]+", "", prompt)

        # Clean up extra whitespace
        prompt = re.sub(r"\s+", " ", prompt).strip()

        return prompt

    def _prepare_images(self, images: list[str]) -> list[str]:
        """
        Prepare images for API - convert local paths to base64 if needed.

        Args:
            images: List of URLs or local file paths

        Returns:
            List of URLs or base64 data URIs
        """
        prepared = []
        for img in images:
            if img.startswith(("http://", "https://")):
                prepared.append(img)
            else:
                # Local file - convert to base64
                prepared.append(self._file_to_base64(img))
        return prepared

    def _file_to_base64(self, filepath: str) -> str:
        """
        Convert local file to base64 data URI.

        Args:
            filepath: Path to local image file

        Returns:
            Base64 data URI string
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {filepath}")

        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()

        # Determine MIME type from extension
        suffix = path.suffix.lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        mime = mime_types.get(suffix, "image/png")

        return f"data:{mime};base64,{data}"
