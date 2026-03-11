#!/usr/bin/env python3
"""
Image Generator via APIframe

Generates images using multiple AI engines (Midjourney, Nano Banana Pro)
with pre-configured art direction templates.

Usage:
    # Using preset templates (Midjourney default)
    python generate_image.py hero-banner
    python generate_image.py feature-banner --feature "AI Interview"
    python generate_image.py og-card

    # Using Nano Banana Pro engine
    python generate_image.py hero-banner --engine nbp
    python generate_image.py hero-banner --engine nbp --resolution 4K

    # Custom prompt (art direction style applied automatically)
    python generate_image.py custom --prompt "your custom prompt here" --ar 16:9

    # Raw prompt (no art direction applied)
    python generate_image.py raw --prompt "your exact prompt --ar 1:1 --style raw"

    # With image references (Midjourney)
    python generate_image.py hero-banner --sref https://example.com/style.jpg
    python generate_image.py custom --prompt "workspace" --sref https://example.com/style.jpg --sw 150
    python generate_image.py custom --prompt "person at desk" --cref https://example.com/char.jpg --cw 75
    python generate_image.py custom --prompt "similar scene" --image-url https://example.com/ref.jpg --iw 1.5

    # Edit existing image (Nano Banana Pro only)
    python generate_image.py edit --input generated-assets/hero.png --prompt "add warm lighting"

    # Pipeline: Generate with MJ, refine with NBP
    python generate_image.py hero-banner --pipeline nbp --refine-prompt "enhance details"

Environment:
    GEMINI_API_KEY:   Google Gemini API key (preferred for Nano Banana Pro)
    APIFRAME_API_KEY: APIframe API key (fallback, also needed for Midjourney)
"""

import argparse
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.request import urlretrieve

import yaml

from dotenv import load_dotenv

from engines import (
    GenerationRequest,
    GenerationResult,
    get_engine,
    ENGINE_ALIASES,
)

# Load environment variables
load_dotenv()

APIFRAME_API_KEY = os.getenv("APIFRAME_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Output directory for downloaded images (relative to current working directory)
OUTPUT_DIR = Path.cwd() / "generated-assets"

# Directory containing this script (used to resolve config paths)
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent


# =============================================================================
# BRAND CONFIG — Single source of truth from brand-guidelines.yaml
# =============================================================================

def _load_brand_config() -> dict:
    """Load brand config from YAML, with hardcoded fallback defaults."""
    config_path = _PROJECT_ROOT / "config" / "brand-guidelines.yaml"
    try:
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except (FileNotFoundError, yaml.YAMLError) as exc:
        print(f"Warning: Could not load brand config ({exc}), using defaults")
        return {}


_BRAND_CONFIG = _load_brand_config()

# Derive style strings from YAML (with hardcoded fallback matching original values)
_prompt_style = _BRAND_CONFIG.get("prompt_style", {})

STYLE_BASE = _prompt_style.get(
    "base",
    "digital illustration style, stylized art, warm color palette, "
    "coral and amber gradient sky, detailed artistic patterns, "
    "whimsical atmosphere, painterly textures, soft warm lighting, "
    "dreamy quality",
)

STYLE_SUFFIX = _prompt_style.get(
    "suffix_midjourney",
    "--style raw --no photorealistic photograph photo",
)

STYLE_SUFFIX_NBP = _prompt_style.get("suffix_nano_banana", "")
STYLE_SUFFIX_GEMINI = _BRAND_CONFIG.get("prompt_style_suffix_gemini", "")

# Brand reference settings
_style_refs = _BRAND_CONFIG.get("style_references", {})
BRAND_REFS_ENABLED = _style_refs.get("enabled", False)
BRAND_SREF_URL = _style_refs.get("midjourney_sref", "")
BRAND_SREF_WEIGHT = _style_refs.get("midjourney_sref_weight", 100)
BRAND_REF_PATHS = _style_refs.get("local_paths", [])
BRAND_STYLE_INSTRUCTION = _style_refs.get("style_instruction", "")

TEMPLATES = {
    "hero-banner": {
        "description": "Landing page hero banner (2560x1440)",
        "aspect_ratio": "16:9",
        "prompt": f"""
stylized illustrated cityscape or landscape, {STYLE_BASE},
warm sunset gradient sky in coral and amber tones,
detailed buildings or structures with artistic patterns,
whimsical dreamy atmosphere, soft warm glow,
CENTER-WEIGHTED composition for responsive cropping,
{STYLE_SUFFIX}
""",
    },
    "og-card": {
        "description": "Social/OG card for sharing (1200x630)",
        "aspect_ratio": "1.91:1",
        "prompt": f"""
abstract developer workspace essence, warm amber glow,
layered paper textures, soft geometric code symbols,
calm focused atmosphere, premium handcrafted feel,
TEXT-SAFE MARGINS (keep edges clear for platform overlays),
golden hour lighting --style raw
""",
    },
    "twitter-card": {
        "description": "Twitter/X card (1200x600)",
        "aspect_ratio": "2:1",
        "prompt": f"""
abstract developer workspace essence, warm amber glow,
layered paper textures, soft geometric code symbols,
calm focused atmosphere, premium handcrafted feel,
TEXT-SAFE MARGINS, golden hour lighting --style raw
""",
    },
    "icon-sheet": {
        "description": "Developer icon concept sheet (1024x1024)",
        "aspect_ratio": "1:1",
        "prompt": f"""
minimal developer icon set, monoline style with organic curves,
subtle hand-drawn imperfection, warm golden accent color,
dark background, code brackets and flow symbols,
consistent stroke weight, soft rounded terminals,
HIGH CONTRAST for small size legibility,
artisanal quality --style raw --no 3d realistic gradient
""",
    },
    "feature-banner": {
        "description": "Feature section banner (1920x640)",
        "aspect_ratio": "3:1",
        "prompt": f"""
abstract representation of [FEATURE], atmospheric depth,
soft focus layers, warm amber and deep charcoal palette,
subtle noise texture overlay, feeling of calm confidence,
HORIZONTAL composition optimized for wide banner,
developer-focused visual metaphor --style raw
""",
        "requires": ["feature"],
    },
    "mobile-hero": {
        "description": "Mobile hero vertical (750x1334)",
        "aspect_ratio": "9:16",
        "prompt": f"""
atmospheric developer moment, vertical composition,
soft golden light from above, subtle paper grain texture,
CENTERED focal point for safe cropping,
calm preparation feeling, artisanal warmth,
muted earth tones --style raw --no text
""",
    },
    "interview-banner": {
        "description": "Interview mode specific banner",
        "aspect_ratio": "16:9",
        "variants": {
            "human-human": f"""
two abstract warm glowing forms in conversation,
soft golden ambient light, collaborative atmosphere,
subtle paper texture, depth and warmth,
feeling of mutual respect and preparation,
muted earth tones {STYLE_SUFFIX}
""",
            "bot-human": f"""
abstract warm glow meeting geometric form,
soft amber light bridging organic and structured,
subtle texture, atmospheric depth,
feeling of supportive AI presence,
human warmth despite technology --style raw --no faces robots
""",
            "bot-bot": f"""
two geometric forms in harmonic dialogue,
soft golden light, structured but warm,
subtle paper texture, layered depth,
feeling of precise orchestration,
technical elegance --style raw --no robots faces
""",
        },
        "requires": ["mode"],
    },
    "card-background": {
        "description": "Card/tile background (800x600)",
        "aspect_ratio": "4:3",
        "prompt": f"""
abstract atmospheric background, {STYLE_BASE},
soft focus, subtle geometric patterns,
warm charcoal base with amber accents,
premium texture overlay --style raw --no text objects
""",
    },
}


def get_api_key() -> str:
    """Get APIframe API key, or empty string if only Gemini is configured."""
    if not APIFRAME_API_KEY and not GEMINI_API_KEY:
        print("Error: No API key set. Provide at least one of:")
        print("  GEMINI_API_KEY=...   (for direct Gemini / Nano Banana Pro)")
        print("  APIFRAME_API_KEY=... (for Midjourney and APIframe-backed NBP)")
        sys.exit(1)
    return APIFRAME_API_KEY or ""


def poll_for_completion(
    engine, task_id: str, timeout: int = 300, interval: int = 5
) -> Optional[GenerationResult]:
    """Poll for task completion with timeout."""
    start_time = time.time()

    print(f"\nWaiting for generation to complete...")

    while time.time() - start_time < timeout:
        result = engine.fetch(task_id)

        if result.status in ("completed", "finished"):
            print(f"\nGeneration complete!")
            return result

        if result.status in ("failed", "error"):
            print(f"\nGeneration failed: {result.raw_response}")
            return None

        # Show progress
        print(f"  Status: {result.status} ({result.percentage}%)", end="\r")
        time.sleep(interval)

    print(f"\nTimeout after {timeout} seconds")
    return None


def download_images(result: GenerationResult, prefix: str = "generated") -> list[Path]:
    """Download generated images to the output directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image_urls = result.image_urls

    if not image_urls:
        print("No images found in result")
        return []

    downloaded = []
    timestamp = int(time.time())

    for i, url in enumerate(image_urls):
        filename = f"{prefix}_{timestamp}_{i + 1}.png"
        filepath = OUTPUT_DIR / filename

        if url.startswith(("http://", "https://")):
            print(f"Downloading: {filename}")
            urlretrieve(url, filepath)
        else:
            # Local file (e.g. from Gemini engine) — copy it
            print(f"Saving: {filename}")
            shutil.copy2(url, filepath)
        downloaded.append(filepath)

    return downloaded


def build_prompt(template_name: str, **kwargs) -> tuple[str, str]:
    """Build a prompt from a template."""
    if template_name not in TEMPLATES:
        print(f"Error: Unknown template '{template_name}'")
        print(f"Available templates: {', '.join(TEMPLATES.keys())}")
        sys.exit(1)

    template = TEMPLATES[template_name]

    # Check required parameters
    required = template.get("requires", [])
    for req in required:
        if req not in kwargs or not kwargs[req]:
            print(f"Error: Template '{template_name}' requires --{req}")
            sys.exit(1)

    # Handle variant templates (like interview-banner)
    if "variants" in template:
        mode = kwargs.get("mode", "human-human")
        if mode not in template["variants"]:
            print(f"Error: Unknown mode '{mode}'")
            print(f"Available modes: {', '.join(template['variants'].keys())}")
            sys.exit(1)
        prompt = template["variants"][mode]
    else:
        prompt = template["prompt"]

    # Replace placeholders
    if "[FEATURE]" in prompt:
        feature = kwargs.get("feature", "Developer Tools")
        prompt = prompt.replace("[FEATURE]", feature)

    return prompt, template["aspect_ratio"]


def apply_art_direction(prompt: str, engine_name: str) -> str:
    """Apply art direction style to a custom prompt if not already styled."""
    # Check if already has style flags (for Midjourney)
    if "--style" in prompt.lower():
        return prompt

    # Pick engine-specific suffix from YAML config
    suffix_map = {
        "midjourney": STYLE_SUFFIX,
        "mj": STYLE_SUFFIX,
        "nano-banana-pro": STYLE_SUFFIX_NBP,
        "nbp": STYLE_SUFFIX_NBP,
        "gemini": STYLE_SUFFIX_GEMINI,
    }
    suffix = suffix_map.get(engine_name, "")

    # Add art direction elements
    if engine_name in ("midjourney", "mj"):
        style_addition = f", {STYLE_BASE}, {suffix}".rstrip(", ")
    else:
        style_addition = f", {STYLE_BASE}"
        if suffix:
            style_addition += f", {suffix}"

    return prompt + style_addition


def list_templates():
    """Print available templates."""
    print("\nAvailable Templates:")
    print("-" * 60)
    for name, template in TEMPLATES.items():
        desc = template["description"]
        ar = template["aspect_ratio"]
        requires = template.get("requires", [])
        req_str = f" (requires: --{', --'.join(requires)})" if requires else ""
        print(f"  {name:20} {ar:8} - {desc}{req_str}")

    if "interview-banner" in TEMPLATES:
        modes = TEMPLATES["interview-banner"].get("variants", {}).keys()
        print(f"\n  Interview banner modes: {', '.join(modes)}")

    print("\nEngines:")
    print("  midjourney (mj)      - Midjourney via APIframe (default)")
    print("  nano-banana-pro (nbp) - Gemini image model, supports editing")
    print("  gemini               - Direct Gemini API (requires GEMINI_API_KEY)")
    print()
    print("  Note: 'nbp' auto-selects Gemini API when GEMINI_API_KEY is set,")
    print("  otherwise falls back to APIframe.")


def execute_pipeline(
    primary_result: GenerationResult,
    pipeline_engine,
    refine_prompt: str,
    aspect_ratio: str,
    resolution: Optional[str] = None,
    brand_references: Optional[list[str]] = None,
    brand_sref: Optional[str] = None,
    brand_sref_weight: int = 100,
    brand_style_instruction: str = "",
) -> Optional[GenerationResult]:
    """
    Post-process primary generation result through secondary engine.

    Returns the refined result, or None on failure.
    """
    image_urls = primary_result.image_urls

    if not image_urls:
        raise ValueError("No images to process in pipeline")

    print(f"\n--- Pipeline: Refining with {pipeline_engine.name} ---")

    # Create editing request for pipeline engine
    request = GenerationRequest(
        prompt=refine_prompt,
        aspect_ratio=aspect_ratio,
        input_images=image_urls,
        resolution=resolution,
        brand_references=brand_references or [],
        brand_sref=brand_sref,
        brand_sref_weight=brand_sref_weight,
        brand_style_instruction=brand_style_instruction,
    )

    # Submit to pipeline engine
    print(f"Submitting to {pipeline_engine.name}...")
    print(f"Refine prompt: {refine_prompt[:100]}...")

    task_id = pipeline_engine.submit(request)
    print(f"Task submitted: {task_id}")

    # Poll for completion
    return poll_for_completion(pipeline_engine, task_id)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images via APIframe (Midjourney, Nano Banana Pro)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s hero-banner
  %(prog)s hero-banner --engine nbp --resolution 4K
  %(prog)s feature-banner --feature "AI Interview"
  %(prog)s interview-banner --mode bot-human
  %(prog)s custom --prompt "a calm workspace" --ar 16:9
  %(prog)s raw --prompt "exact prompt --ar 1:1 --v 6"
  %(prog)s edit --input image.png --prompt "add warm lighting"
  %(prog)s hero-banner --pipeline nbp --refine-prompt "enhance details"
  %(prog)s --list
        """,
    )

    parser.add_argument(
        "template",
        nargs="?",
        help="Template name, 'custom'/'raw' for custom prompts, or 'edit' for editing",
    )
    parser.add_argument(
        "--prompt", "-p", help="Custom prompt (for 'custom', 'raw', or 'edit')"
    )
    parser.add_argument(
        "--ar",
        "--aspect-ratio",
        default="1:1",
        help="Aspect ratio for custom prompts (default: 1:1)",
    )
    parser.add_argument(
        "--feature", "-f", help="Feature name for feature-banner template"
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=["human-human", "bot-human", "bot-bot"],
        default="human-human",
        help="Interview mode for interview-banner template",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Don't download images, just print URLs",
    )
    parser.add_argument(
        "--output-prefix",
        "-o",
        default=None,
        help="Prefix for downloaded files (default: template name)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds (default: 300)",
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="List available templates"
    )

    # Engine selection
    parser.add_argument(
        "--engine",
        "-e",
        choices=list(ENGINE_ALIASES.keys()),
        default="midjourney",
        help="Image generation engine (default: midjourney)",
    )

    # Nano Banana Pro specific
    parser.add_argument(
        "--resolution",
        choices=["1K", "2K", "4K"],
        default=None,
        help="Output resolution for Nano Banana Pro (default: 2K)",
    )

    # Input images for editing
    parser.add_argument(
        "--input",
        "-i",
        action="append",
        dest="input_images",
        help="Input image path or URL for editing (can be specified multiple times)",
    )

    # Pipeline workflow
    parser.add_argument(
        "--pipeline",
        choices=["nbp", "nano-banana-pro", "gemini"],
        help="Post-process result through specified engine",
    )
    parser.add_argument(
        "--refine-prompt",
        help="Refinement prompt for pipeline post-processing",
    )

    # Brand reference control
    parser.add_argument(
        "--no-brand-ref",
        action="store_true",
        help="Skip automatic brand style references for this invocation",
    )

    # Midjourney image reference arguments
    parser.add_argument(
        "--sref",
        help="Style reference image URL (Midjourney: matches artistic style)",
    )
    parser.add_argument(
        "--sw",
        type=int,
        default=100,
        help="Style weight 0-1000 (default: 100)",
    )
    parser.add_argument(
        "--cref",
        help="Character reference image URL (Midjourney: maintains character identity)",
    )
    parser.add_argument(
        "--cw",
        type=int,
        default=100,
        help="Character weight 0-100 (default: 100)",
    )
    parser.add_argument(
        "--image-url",
        help="Image URL to include in prompt (Midjourney: influences composition)",
    )
    parser.add_argument(
        "--iw",
        type=float,
        default=1.0,
        help="Image weight 0-2 (default: 1.0)",
    )

    args = parser.parse_args()

    if args.list:
        list_templates()
        return

    if not args.template:
        parser.print_help()
        print("\n")
        list_templates()
        return

    # Get API key
    api_key = get_api_key()

    # Handle edit command
    if args.template == "edit":
        if not args.prompt:
            print("Error: 'edit' requires --prompt")
            sys.exit(1)
        if not args.input_images:
            print("Error: 'edit' requires at least one --input image")
            sys.exit(1)

        # Edit always uses Nano Banana Pro
        engine = get_engine("nano-banana-pro", api_key, gemini_api_key=GEMINI_API_KEY)
        print(f"\nUsing engine: {engine.name} (editing)")

        request = GenerationRequest(
            prompt=args.prompt,
            aspect_ratio=args.ar,
            resolution=args.resolution,
            input_images=args.input_images,
        )

        print(f"Input images: {len(args.input_images)}")
        for img in args.input_images:
            print(f"  - {img}")

        task_id = engine.submit(request)
        print(f"Task submitted: {task_id}")

        result = poll_for_completion(engine, task_id, timeout=args.timeout)

    else:
        # Get primary engine
        engine = get_engine(args.engine, api_key, gemini_api_key=GEMINI_API_KEY)
        print(f"\nUsing engine: {engine.name}")

        # Build prompt based on template type
        if args.template == "raw":
            if not args.prompt:
                print("Error: 'raw' template requires --prompt")
                sys.exit(1)
            prompt = args.prompt
            aspect_ratio = args.ar
        elif args.template == "custom":
            if not args.prompt:
                print("Error: 'custom' template requires --prompt")
                sys.exit(1)
            prompt = apply_art_direction(args.prompt, args.engine)
            aspect_ratio = args.ar
        else:
            prompt, aspect_ratio = build_prompt(
                args.template, feature=args.feature, mode=args.mode
            )

        # Resolve brand references if enabled
        brand_references = []
        brand_sref = None
        brand_sref_weight = BRAND_SREF_WEIGHT
        brand_style_instruction = ""

        use_brand_refs = (
            BRAND_REFS_ENABLED
            and not args.no_brand_ref
            and args.template != "raw"
        )

        if use_brand_refs:
            # Resolve local paths to absolute
            for rel_path in BRAND_REF_PATHS:
                abs_path = _PROJECT_ROOT / rel_path
                if abs_path.exists():
                    brand_references.append(str(abs_path))

            # Only set brand_sref if user didn't provide --sref (user wins)
            if not args.sref and BRAND_SREF_URL:
                brand_sref = BRAND_SREF_URL

            brand_style_instruction = BRAND_STYLE_INSTRUCTION

        # Create generation request
        request = GenerationRequest(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            resolution=args.resolution,
            style_reference=args.sref,
            style_weight=args.sw,
            character_reference=args.cref,
            character_weight=args.cw,
            image_prompt=args.image_url,
            image_weight=args.iw,
            brand_references=brand_references,
            brand_sref=brand_sref,
            brand_sref_weight=brand_sref_weight,
            brand_style_instruction=brand_style_instruction,
        )

        # Submit and wait
        print(f"Aspect ratio: {aspect_ratio}")
        if args.resolution:
            print(f"Resolution: {args.resolution}")

        built_prompt = engine.build_prompt(request)
        print(f"Prompt: {built_prompt[:100]}...")

        task_id = engine.submit(request)
        print(f"Task submitted: {task_id}")

        result = poll_for_completion(engine, task_id, timeout=args.timeout)

        # Handle pipeline if requested
        if result and args.pipeline:
            if not args.refine_prompt:
                print("Warning: --pipeline specified without --refine-prompt")
                print("Using default refinement: 'enhance details and quality'")
                args.refine_prompt = "enhance details and quality"

            pipeline_engine = get_engine(args.pipeline, api_key, gemini_api_key=GEMINI_API_KEY)

            # Save intermediate result in case pipeline fails
            if not args.no_download:
                prefix = f"{args.output_prefix or args.template or 'generated'}_intermediate"
                intermediate_files = download_images(result, prefix=prefix)
                print(f"\nIntermediate saved to: {OUTPUT_DIR}")

            pipeline_result = execute_pipeline(
                result,
                pipeline_engine,
                args.refine_prompt,
                aspect_ratio,
                args.resolution,
                brand_references=brand_references,
                brand_sref=brand_sref,
                brand_sref_weight=brand_sref_weight,
                brand_style_instruction=brand_style_instruction,
            )

            if pipeline_result:
                result = pipeline_result
            else:
                print("\nPipeline failed, using intermediate result")

    if not result:
        print("Failed to generate image")
        sys.exit(1)

    # Output results
    print(f"\nGenerated {len(result.image_urls)} image(s):")
    for url in result.image_urls:
        print(f"  {url}")

    # Download if requested
    if not args.no_download:
        prefix = args.output_prefix or args.template or "generated"
        downloaded = download_images(result, prefix=prefix)
        print(f"\nDownloaded to: {OUTPUT_DIR}")
        for path in downloaded:
            print(f"  {path.name}")


if __name__ == "__main__":
    main()
