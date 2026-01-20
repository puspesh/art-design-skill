# Art Design Skill

A Claude Code skill for art direction and visual identity, with integrated Midjourney image generation via APIframe.

## Features

- **Visual Identity System**: "Calm Confidence" art direction with defined textures, colors, and patterns
- **Midjourney Integration**: Generate images using pre-configured templates via APIframe API
- **Prompt Templates**: Hero banners, OG cards, icons, feature banners, and more
- **Image References**: Use style reference (`--sref`), character reference (`--cref`), or image prompts to match existing images
- **Local Asset Management**: Download and organize generated images

## Installation

### As a Claude Code Plugin

Add to your Claude Code settings:

```json
{
  "plugins": [
    "github:puspesh/art-design-skill"
  ]
}
```

### Manual Installation

1. Clone this repository
2. Copy the `skills/` directory to `~/.claude/skills/`

## Usage

### Invoke the Skill

The skill activates automatically when working on visual assets, or invoke manually:

```
/art-direction-visual-identity
```

### Generate Images

```bash
# List available templates
python scripts/generate_image.py --list

# Generate using preset templates
python scripts/generate_image.py hero-banner
python scripts/generate_image.py og-card
python scripts/generate_image.py icon-sheet
python scripts/generate_image.py interview-banner --mode bot-human

# Custom prompt with art direction applied
python scripts/generate_image.py custom --prompt "your concept here" --ar 16:9

# Raw prompt (full control)
python scripts/generate_image.py raw --prompt "exact midjourney prompt --ar 1:1"
```

### Environment Setup

Set your APIframe API key:

```bash
export APIFRAME_API_KEY=your_key_here
```

Or create a `.env` file:

```
APIFRAME_API_KEY=your_key_here
```

## Templates

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

## Image References

Generate images that match the style or composition of existing images:

```bash
# Style reference - match artistic style of an image
python scripts/generate_image.py hero-banner --sref https://example.com/style.jpg
python scripts/generate_image.py custom --prompt "workspace" --sref https://example.com/style.jpg --sw 150

# Character reference - maintain character identity
python scripts/generate_image.py custom --prompt "person at desk" --cref https://example.com/char.jpg --cw 75

# Image prompt - influence composition
python scripts/generate_image.py custom --prompt "similar scene" --image-url https://example.com/ref.jpg --iw 1.5
```

| Option | Description | Range |
|--------|-------------|-------|
| `--sref` | Style reference image URL | - |
| `--sw` | Style weight | 0-1000 (default: 100) |
| `--cref` | Character reference image URL | - |
| `--cw` | Character weight | 0-100 (default: 100) |
| `--image-url` | Image prompt URL | - |
| `--iw` | Image weight | 0-2 (default: 1.0) |

## Visual Identity

**Core Feeling**: Calm Confidence - "The deep breath before you speak"

**Key Elements**:
- Warm darks (deep charcoal, not pure black)
- Golden/amber accents
- Paper grain textures
- Atmospheric depth
- Artisanal, hand-crafted feel

See the full skill documentation for complete art direction guidelines.

## Dependencies

```bash
pip install requests python-dotenv
```

## License

MIT
