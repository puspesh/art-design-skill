"""
Midjourney image generation engine via APIframe.
"""

import requests

from .base import BaseEngine, GenerationRequest, GenerationResult


class MidjourneyEngine(BaseEngine):
    """Midjourney image generation via APIframe."""

    ENDPOINT = "https://api.apiframe.pro/imagine"
    FETCH_ENDPOINT = "https://api.apiframe.pro/fetch"

    def __init__(self, api_key: str):
        """
        Initialize Midjourney engine.

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
        return "midjourney"

    @property
    def supports_editing(self) -> bool:
        return False

    def submit(self, request: GenerationRequest) -> str:
        """Submit imagine request to Midjourney via APIframe."""
        prompt = self.build_prompt(request)

        payload = {
            "prompt": prompt.strip().replace("\n", " "),
            "aspect_ratio": request.aspect_ratio,
        }

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
        """Fetch result for a Midjourney task."""
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
        """Build Midjourney prompt with all reference parameters."""
        prompt = request.prompt.strip().replace("\n", " ")

        # Add image URL at start if provided (influences composition)
        if request.image_prompt:
            prompt = f"{request.image_prompt} {prompt}"
            if request.image_weight != 1.0:
                prompt += f" --iw {request.image_weight}"

        # Add style reference (user-provided takes priority over brand)
        if request.style_reference:
            prompt += f" --sref {request.style_reference}"
            if request.style_weight != 100:
                prompt += f" --sw {request.style_weight}"
        elif request.brand_sref:
            prompt += f" --sref {request.brand_sref}"
            if request.brand_sref_weight != 100:
                prompt += f" --sw {request.brand_sref_weight}"

        # Add character reference
        if request.character_reference:
            prompt += f" --cref {request.character_reference}"
            if request.character_weight != 100:
                prompt += f" --cw {request.character_weight}"

        return prompt
