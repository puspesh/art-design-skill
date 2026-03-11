"""
Nano Banana Pro engine via Google Gemini API (direct).

Uses the google-genai SDK for synchronous image generation and editing,
bypassing APIframe. Falls back to APIframe variant when GEMINI_API_KEY
is not available.
"""

import base64
import re
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

from .base import BaseEngine, GenerationRequest, GenerationResult

# Imagen model for generation
IMAGEN_MODEL = "imagen-4.0-generate-001"
# Nano Banana Pro model for editing (understands images + text, supports image output)
EDIT_MODEL = "nano-banana-pro-preview"


class GeminiNanoBananaProEngine(BaseEngine):
    """Nano Banana Pro via direct Google Gemini API."""

    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)
        self._results: dict[str, GenerationResult] = {}

    @property
    def name(self) -> str:
        return "gemini-nano-banana-pro"

    @property
    def supports_editing(self) -> bool:
        return True

    def submit(self, request: GenerationRequest) -> str:
        """Generate image synchronously and store result."""
        prompt = self.build_prompt(request)

        # Prepend brand style instruction when brand refs are active
        if request.brand_style_instruction and request.brand_references:
            prompt = f"{request.brand_style_instruction} {prompt}"

        try:
            if request.input_images:
                image_paths = self._edit(prompt, request)
            elif request.brand_references:
                # Route through multimodal path with brand reference images
                image_paths = self._edit(prompt, request, override_images=request.brand_references)
            else:
                image_paths = self._generate(prompt, request)
        except Exception as exc:
            task_id = str(uuid.uuid4())
            self._results[task_id] = GenerationResult(
                task_id=task_id,
                status="error",
                raw_response={"error": str(exc)},
            )
            return task_id

        task_id = str(uuid.uuid4())
        if image_paths:
            self._results[task_id] = GenerationResult(
                task_id=task_id,
                status="completed",
                image_urls=image_paths,
                percentage="100",
            )
        else:
            self._results[task_id] = GenerationResult(
                task_id=task_id,
                status="error",
                raw_response={"error": "No images in response"},
            )

        return task_id

    def fetch(self, task_id: str) -> GenerationResult:
        """Return stored result (generation already completed in submit)."""
        if task_id in self._results:
            return self._results[task_id]
        return GenerationResult(
            task_id=task_id,
            status="error",
            raw_response={"error": f"Unknown task_id: {task_id}"},
        )

    def build_prompt(self, request: GenerationRequest) -> str:
        """Strip Midjourney-specific flags from prompt."""
        prompt = request.prompt.strip().replace("\n", " ")

        prompt = re.sub(r"--style\s+\w+", "", prompt)
        prompt = re.sub(r"--no\s+[\w\s]+(?=--|$)", "", prompt)
        prompt = re.sub(r"--v\s+[\d.]+", "", prompt)
        prompt = re.sub(r"--ar\s+[\d:.]+", "", prompt)
        prompt = re.sub(r"--sref\s+\S+", "", prompt)
        prompt = re.sub(r"--sw\s+\d+", "", prompt)
        prompt = re.sub(r"--cref\s+\S+", "", prompt)
        prompt = re.sub(r"--cw\s+\d+", "", prompt)
        prompt = re.sub(r"--iw\s+[\d.]+", "", prompt)

        return re.sub(r"\s+", " ", prompt).strip()

    # ------------------------------------------------------------------
    # Generation (text → image) via Imagen
    # ------------------------------------------------------------------

    def _generate(self, prompt: str, request: GenerationRequest) -> list[str]:
        """Text-to-image using generate_images()."""
        config = types.GenerateImagesConfig(
            aspectRatio=request.aspect_ratio,
            numberOfImages=1,
        )

        response = self._client.models.generate_images(
            model=IMAGEN_MODEL,
            prompt=prompt,
            config=config,
        )

        saved: list[str] = []
        if response.generated_images:
            for gi in response.generated_images:
                if gi.image:
                    tmp = tempfile.NamedTemporaryFile(
                        suffix=".png", prefix="gemini_", delete=False
                    )
                    tmp.close()
                    gi.image.save(tmp.name)
                    saved.append(tmp.name)
        return saved

    # ------------------------------------------------------------------
    # Editing (image + text → image) via Gemini multimodal
    # ------------------------------------------------------------------

    def _edit(self, prompt: str, request: GenerationRequest, override_images: Optional[list[str]] = None) -> list[str]:
        """Image editing using generate_content() with multimodal input."""
        images = override_images if override_images is not None else request.input_images
        contents = self._build_edit_contents(prompt, images)

        config = types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        )

        response = self._client.models.generate_content(
            model=EDIT_MODEL,
            contents=contents,
            config=config,
        )

        saved: list[str] = []
        if not response.candidates:
            return saved

        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                suffix = ".png"
                if "jpeg" in part.inline_data.mime_type:
                    suffix = ".jpg"
                elif "webp" in part.inline_data.mime_type:
                    suffix = ".webp"

                tmp = tempfile.NamedTemporaryFile(
                    suffix=suffix, prefix="gemini_edit_", delete=False
                )
                tmp.write(part.inline_data.data)
                tmp.close()
                saved.append(tmp.name)

        return saved

    def _build_edit_contents(self, prompt: str, image_paths: list[str]) -> list:
        """Build multimodal contents list for image editing."""
        from PIL import Image as PILImage

        contents = [prompt]
        for img_path in image_paths:
            if img_path.startswith(("http://", "https://")):
                contents.append(types.Part.from_uri(img_path, mime_type="image/png"))
            elif img_path.startswith("data:"):
                header, data = img_path.split(",", 1)
                mime = header.split(":")[1].split(";")[0]
                contents.append(
                    types.Part.from_bytes(base64.b64decode(data), mime_type=mime)
                )
            else:
                contents.append(PILImage.open(img_path))
        return contents
