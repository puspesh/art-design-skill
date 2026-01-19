# Art Design Skill

A Claude Code skill for art direction and visual identity, with integrated Midjourney image generation via APIframe.

## Features

- **Visual Identity System**: "Calm Confidence" art direction with defined textures, colors, and patterns
- **Midjourney Integration**: Generate images using pre-configured templates via APIframe API
- **Prompt Templates**: Hero banners, OG cards, icons, feature banners, and more
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
