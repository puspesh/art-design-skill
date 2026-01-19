#!/usr/bin/env python3
"""
Midjourney Image Generator via APIframe

Generates images using the APIframe.ai Midjourney API with
pre-configured art direction templates for the interview platform.

Usage:
    # Using preset templates
    python generate_image.py hero-banner
    python generate_image.py feature-banner --feature "AI Interview"
    python generate_image.py og-card
    python generate_image.py icon-sheet
    python generate_image.py interview-banner --mode bot-human

    # Custom prompt (art direction style applied automatically)
    python generate_image.py custom --prompt "your custom prompt here" --ar 16:9

    # Raw prompt (no art direction applied)
    python generate_image.py raw --prompt "your exact prompt --ar 1:1 --style raw"

Environment:
    APIFRAME_API_KEY: Your APIframe API key (required)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.request import urlretrieve

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

APIFRAME_API_KEY = os.getenv("APIFRAME_API_KEY")
APIFRAME_BASE_URL = "https://api.apiframe.pro"

# Output directory for downloaded images (relative to current working directory)
OUTPUT_DIR = Path.cwd() / "generated-assets"


# =============================================================================
# ART DIRECTION TEMPLATES
# Based on the Visual Identity System - "Calm Confidence"
# =============================================================================

# Core style elements applied to all templates
STYLE_BASE = """
soft golden ambient light, subtle paper texture,
muted warm earth tones, artisanal crafted quality,
atmospheric depth, layered elements
""".strip().replace("\n", " ")

STYLE_SUFFIX = "--style raw --no people faces text"

TEMPLATES = {
    "hero-banner": {
        "description": "Landing page hero banner (2560x1440)",
        "aspect_ratio": "16:9",
        "prompt": f"""
atmospheric developer sanctuary, {STYLE_BASE},
depth of field, code editor glow in distance,
feeling of quiet preparation before important moment,
CENTER-WEIGHTED composition for responsive cropping,
cinematic {STYLE_SUFFIX}
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


def get_headers() -> dict:
    """Get API request headers."""
    if not APIFRAME_API_KEY:
        print("Error: APIFRAME_API_KEY not set in environment")
        print("Add it to your .env file: APIFRAME_API_KEY=your_key_here")
        sys.exit(1)

    return {
        "Content-Type": "application/json",
        "Authorization": APIFRAME_API_KEY,
    }


def submit_imagine(prompt: str, aspect_ratio: str = "1:1") -> str:
    """Submit an imagine request and return the task_id."""
    url = f"{APIFRAME_BASE_URL}/imagine"

    payload = {
        "prompt": prompt.strip().replace("\n", " "),
        "aspect_ratio": aspect_ratio,
    }

    print(f"\nSubmitting prompt to Midjourney...")
    print(f"Aspect ratio: {aspect_ratio}")
    print(f"Prompt: {payload['prompt'][:100]}...")

    response = requests.post(url, headers=get_headers(), json=payload)

    if response.status_code != 200:
        print(f"Error: API returned status {response.status_code}")
        print(response.text)
        sys.exit(1)

    data = response.json()
    task_id = data.get("task_id")

    if not task_id:
        print(f"Error: No task_id in response: {data}")
        sys.exit(1)

    print(f"Task submitted: {task_id}")
    return task_id


def fetch_result(task_id: str) -> dict:
    """Fetch the result of a task."""
    url = f"{APIFRAME_BASE_URL}/fetch"
    payload = {"task_id": task_id}

    response = requests.post(url, headers=get_headers(), json=payload)

    if response.status_code != 200:
        return {"status": "error", "message": response.text}

    return response.json()


def poll_for_completion(
    task_id: str, timeout: int = 300, interval: int = 5
) -> Optional[dict]:
    """Poll for task completion with timeout."""
    start_time = time.time()

    print(f"\nWaiting for generation to complete...")

    while time.time() - start_time < timeout:
        result = fetch_result(task_id)
        status = result.get("status", "unknown")
        percentage = result.get("percentage", "0")

        if status in ("completed", "finished"):
            print(f"\nGeneration complete!")
            return result

        if status == "failed" or status == "error":
            print(f"\nGeneration failed: {result}")
            return None

        # Show progress
        print(f"  Status: {status} ({percentage}%)", end="\r")
        time.sleep(interval)

    print(f"\nTimeout after {timeout} seconds")
    return None


def download_images(result: dict, prefix: str = "generated") -> list[Path]:
    """Download generated images to the output directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image_urls = result.get("image_urls", [])
    if not image_urls:
        # Try single image URL
        single_url = result.get("original_image_url")
        if single_url:
            image_urls = [single_url]

    if not image_urls:
        print("No images found in result")
        return []

    downloaded = []
    timestamp = int(time.time())

    for i, url in enumerate(image_urls):
        filename = f"{prefix}_{timestamp}_{i + 1}.png"
        filepath = OUTPUT_DIR / filename

        print(f"Downloading: {filename}")
        urlretrieve(url, filepath)
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


def apply_art_direction(prompt: str) -> str:
    """Apply art direction style to a custom prompt if not already styled."""
    # Check if already has style flags
    if "--style" in prompt.lower():
        return prompt

    # Add art direction elements
    style_addition = f", {STYLE_BASE}, --style raw"
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


def main():
    parser = argparse.ArgumentParser(
        description="Generate Midjourney images via APIframe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s hero-banner
  %(prog)s feature-banner --feature "AI Interview"
  %(prog)s interview-banner --mode bot-human
  %(prog)s custom --prompt "a calm workspace" --ar 16:9
  %(prog)s raw --prompt "exact prompt --ar 1:1 --v 6"
  %(prog)s --list
        """,
    )

    parser.add_argument(
        "template",
        nargs="?",
        help="Template name or 'custom'/'raw' for custom prompts",
    )
    parser.add_argument(
        "--prompt", "-p", help="Custom prompt (for 'custom' or 'raw' template)"
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

    args = parser.parse_args()

    if args.list:
        list_templates()
        return

    if not args.template:
        parser.print_help()
        print("\n")
        list_templates()
        return

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
        prompt = apply_art_direction(args.prompt)
        aspect_ratio = args.ar
    else:
        prompt, aspect_ratio = build_prompt(
            args.template, feature=args.feature, mode=args.mode
        )

    # Submit and wait
    task_id = submit_imagine(prompt, aspect_ratio)
    result = poll_for_completion(task_id, timeout=args.timeout)

    if not result:
        print("Failed to generate image")
        sys.exit(1)

    # Output results
    image_urls = result.get("image_urls", [])
    if not image_urls:
        single_url = result.get("original_image_url")
        if single_url:
            image_urls = [single_url]

    print(f"\nGenerated {len(image_urls)} image(s):")
    for url in image_urls:
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
