# Art Design Plugin

A Claude Code plugin for art direction and visual identity, with integrated image generation via Midjourney and Nano Banana Pro (Gemini).

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- **Multi-Engine Support**: Generate with Midjourney or Nano Banana Pro
- **Visual Identity System**: Customizable art direction (default: warm illustration style)
- **Image Editing**: Edit and refine images with natural language
- **Pipeline Workflows**: Generate with MJ, refine with NBP
- **Customizable Brand**: YAML-based brand guidelines you can override
- **Image Review Agent**: Automated quality checks against brand standards
- **Prompt Templates**: Pre-configured templates for common asset types

## Installation

### From GitHub

Add to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "plugins": ["github:puspesh/art-design-skill"]
}
```

### Manual Installation

1. Clone this repository
2. Run Claude Code with the plugin:
   ```bash
   claude --plugin-dir ./art-design-skill
   ```

## Quick Start

### 1. Set Up API Key

```bash
# For Nano Banana Pro via Gemini (recommended)
export GEMINI_API_KEY=your_gemini_key_here

# For Midjourney (and APIframe-backed NBP fallback)
export APIFRAME_API_KEY=your_apiframe_key_here
```

Or create a `.env` file:
```
GEMINI_API_KEY=your_gemini_key_here
APIFRAME_API_KEY=your_apiframe_key_here
```

### 2. Generate Images

```bash
# List available templates
python scripts/generate_image.py --list

# Generate a hero banner
python scripts/generate_image.py hero-banner

# Generate with Nano Banana Pro
python scripts/generate_image.py hero-banner --engine nbp --resolution 4K
```

### 3. Use Pipeline Refinement

```bash
# Generate with Midjourney, refine with Nano Banana Pro
python scripts/generate_image.py hero-banner \
  --pipeline nbp \
  --refine-prompt "add subtle paper texture and warm golden overlay"
```

### 4. Edit Existing Images

```bash
python scripts/generate_image.py edit \
  --input generated-assets/hero.png \
  --prompt "add atmospheric fog and warm lighting"
```

## Available Templates

| Template | Aspect Ratio | Use Case |
|----------|--------------|----------|
| `hero-banner` | 16:9 | Landing page hero |
| `og-card` | 1.91:1 | Social/OG sharing |
| `twitter-card` | 2:1 | Twitter/X cards |
| `icon-sheet` | 1:1 | Developer icons |
| `feature-banner` | 3:1 | Feature sections |
| `mobile-hero` | 9:16 | Mobile-first contexts |
| `interview-banner` | 16:9 | Interview mode specific |
| `card-background` | 4:3 | Card/tile backgrounds |

## Engines

| Engine | Alias | Capabilities |
|--------|-------|--------------|
| Midjourney | `mj` | High-quality generation, style references |
| Nano Banana Pro | `nbp` | Generation, editing, 1K-4K resolution |
| Gemini (direct) | `gemini` | Direct Gemini API, no APIframe needed |

> **Fallback behaviour**: `--engine nbp` auto-selects the direct Gemini API when `GEMINI_API_KEY` is set. If only `APIFRAME_API_KEY` is available it falls back to APIframe.

## Customization

### Brand Guidelines

Edit `config/brand-guidelines.yaml` to define your own visual identity:

```yaml
name: "Your Brand"
tagline: "Your tagline"

feelings:
  target: ["Clean", "Modern", "Professional"]
  avoid: ["Cluttered", "Dated"]

colors:
  primary:
    hex: "#0066FF"

prompt_style:
  base: "your style descriptors here"
```

See [docs/customizing-brand.md](docs/customizing-brand.md) for full guide.

### Review Criteria

Edit `config/review-criteria.yaml` to define quality standards:

```yaml
on_failure:
  action: "auto_regenerate"  # or "suggest_refinement" or "warn_only"
  max_regeneration_attempts: 2

categories:
  color_warmth:
    weight: 1.0
    required: true
```

## Documentation

- [Workflows Guide](docs/workflows.md) - Detailed workflow examples
- [Customizing Brand](docs/customizing-brand.md) - Brand configuration
- [Extending the Plugin](docs/extending.md) - Add skills, engines, templates

## Image Reference Options (Midjourney)

| Option | Description | Range |
|--------|-------------|-------|
| `--sref` | Style reference image URL | - |
| `--sw` | Style weight | 0-1000 (default: 100) |
| `--cref` | Character reference image URL | - |
| `--cw` | Character weight | 0-100 (default: 100) |
| `--image-url` | Image prompt URL | - |
| `--iw` | Image weight | 0-2 (default: 1.0) |

## Visual Identity (Default)

**Core Feeling**: Whimsical warmth — stylized illustration with a fairground aesthetic

**Key Elements**:
- Digital illustration style (not photorealistic)
- Coral and amber gradient skies
- Painterly textures and soft gradients
- Warm, dreamy atmosphere
- Detailed artistic patterns

Customize via `config/brand-guidelines.yaml` — see [docs/customizing-brand.md](docs/customizing-brand.md).

## Dependencies

```bash
pip install requests python-dotenv
```

## License

MIT

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add your changes
4. Update CHANGELOG.md
5. Submit a pull request

See [docs/extending.md](docs/extending.md) for development guide.
