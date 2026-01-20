---
name: art-direction-visual-identity
description: Use when generating banners, icons, artwork, or any visual assets. Provides atmosphere definition, prompt templates, image generation script execution, and local asset management.
version: 2.0.0
author: puspesh
date: 2025-01-19
---

# Art Direction: Visual Identity System

## Trigger Conditions

This skill activates when you need to:

- Generate banners, icons, or visual assets
- Create consistent branded imagery using Midjourney
- Access or review previously generated images
- Apply the "Calm Confidence" visual identity to new assets
- Design developer-focused visual metaphors

**Keywords**: banner, icon, hero image, og card, visual asset, midjourney, generate image, artwork, branding

---

## Solution Overview

### 1. Image Generation via Script

Use the `generate_image.py` script to generate Midjourney images with pre-configured art direction.

**Script Location**: `scripts/generate_image.py` (relative to this skill's repo)

**Output Directory**: `generated-assets/` (created automatically)

### Available Commands

```bash
# List all available templates
python scripts/generate_image.py --list

# Generate using preset templates
python scripts/generate_image.py hero-banner
python scripts/generate_image.py og-card
python scripts/generate_image.py twitter-card
python scripts/generate_image.py icon-sheet
python scripts/generate_image.py mobile-hero
python scripts/generate_image.py card-background

# Feature banner (requires --feature)
python scripts/generate_image.py feature-banner --feature "Meeting notes"
python scripts/generate_image.py feature-banner --feature "Code Review"

# Custom prompt with art direction applied automatically
python scripts/generate_image.py custom --prompt "your concept here" --ar 16:9

# Raw prompt (no art direction, full control)
python scripts/generate_image.py raw --prompt "exact midjourney prompt --ar 1:1 --v 6"
```

**Options**:
- `--no-download`: Only show URLs, don't download images
- `--output-prefix`, `-o`: Custom filename prefix
- `--timeout`: Generation timeout in seconds (default: 300)

### 2. Accessing Generated Images

**View generated assets**:
```bash
# List all generated images
ls -la generated-assets/

# View most recent images (by modification time)
ls -lt generated-assets/ | head -10
```

**Read/View an image**: Use the Read tool on any image file path to view it visually.

**Image naming convention**: `{template}_{timestamp}_{variant}.png`

### 3. Environment Setup

Requires `APIFRAME_API_KEY` environment variable:

```bash
export APIFRAME_API_KEY=your_key_here
```

Or create a `.env` file in the script directory:
```
APIFRAME_API_KEY=your_key_here
```

### 4. Image Reference Features

Generate images that match the style or composition of existing images.

#### Style Reference (--sref)
Match the artistic style, colors, and aesthetic of a reference image:
```bash
# Apply style from a reference image to a template
python scripts/generate_image.py hero-banner --sref https://example.com/style.jpg

# Custom prompt with style reference and weight control
python scripts/generate_image.py custom --prompt "developer workspace" --sref https://example.com/style.jpg --sw 150
```
- `--sref`: URL of the style reference image
- `--sw`: Style weight 0-1000 (default: 100, higher = stronger style influence)

#### Character Reference (--cref)
Maintain consistent character identity across generations:
```bash
python scripts/generate_image.py custom --prompt "person working at desk" --cref https://example.com/character.jpg --cw 75
```
- `--cref`: URL of the character reference image
- `--cw`: Character weight 0-100 (default: 100, lower = focus only on face)

#### Image Prompt (--image-url)
Use an image to influence composition and content:
```bash
python scripts/generate_image.py custom --prompt "similar atmospheric scene" --image-url https://example.com/reference.jpg --iw 1.5
```
- `--image-url`: URL of the reference image (added to start of prompt)
- `--iw`: Image weight 0-2 (default: 1.0)

#### Combining References
You can combine multiple reference types:
```bash
python scripts/generate_image.py custom \
  --prompt "warm workspace" \
  --sref https://example.com/style.jpg \
  --image-url https://example.com/composition.jpg \
  --ar 16:9
```

---

## The Visual North Star

**Core Feeling**: Calm Confidence

> "The deep breath before you speak"

- Reducing anxiety in high-stakes moments
- Technical precision without coldness
- Spaciousness and breathing room
- Prepared, not anxious
- Open air, not fluorescent lights
- The moment before a confident answer

**Style Direction**: Subtle Depth & Texture
- Artisanal, hand-crafted feel (not sterile SaaS defaults)
- Atmospheric depth without heaviness
- Developer/engineering context with human warmth

---

## Verification Steps

Before finalizing any visual asset:

1. [ ] Run the Feeling Test (see below)
2. [ ] Check texture (not flat)
3. [ ] Verify warm colors (not sterile)
4. [ ] Confirm depth (layers, soft shadows)
5. [ ] For icons: hand-crafted imperfection present
6. [ ] For banners: focal point center-weighted for responsive cropping
7. [ ] File size within guidelines
8. [ ] Consistent with existing design system

### The Feeling Test

```
Ask: "What does this make you feel?"

Target responses:
  "Prepared"
  "Calm"
  "Focused"
  "Professional but warm"
  "Confident"
  "Grounded"

Red flags:
  "Sterile"
  "Generic"
  "Anxious"
  "Corporate"
  "Cold"
  "Frantic"
```

---

## Visual Vocabulary

### Textures
- Subtle paper grain
- Soft noise overlays
- Atmospheric gradients
- Layered depth (not flat)

### Colors
- **Warm darks**: Deep charcoal, never pure black (`#0a0a0a` not `#000000`)
- **Golden accents**: Like candlelight, amber warmth
- **Muted earth tones**: Soft browns, warm grays
- **Intermediate tones**: Soften harsh contrasts

### Motion
- Slow, breathing animations
- Gentle pulses (not frantic loading spinners)
- Smooth state transitions
- Organic easing curves

### Depth
- Layered elements with soft shadows
- Atmospheric perspective
- Subtle blur for background elements
- Never completely flat

---

## Developer Icon Vocabulary

### Code & Syntax Theme
- **Brackets** `{ }` `[ ]` `< >` - with organic curves, not rigid angles
- **Function symbols** - abstract representations of inputs -> outputs
- **Variable containers** - soft-edged boxes suggesting state
- **Syntax highlighting motifs** - color blocks representing code structure

### Infrastructure Theme
- **Server/node representations** - warm glowing cores, not cold boxes
- **API connections** - flowing lines suggesting data movement
- **Database symbols** - layered depth, geological feel
- **Cloud patterns** - atmospheric, not corporate clip-art

### Workflow Theme
- **Git branch visualizations** - organic tree-like growth
- **Pipeline flows** - river-like progression, not industrial conveyor
- **Collaboration nodes** - overlapping presence, shared space
- **State transitions** - breathing animations between states

### Icon Design Rules
1. Add subtle imperfection - hand-drawn feel
2. Consistent stroke width with intentional variation at joints
3. Rounded terminals, not sharp cuts
4. Warm glow effects over flat fills
5. Monoline style with organic curves
6. High contrast for small size legibility

**Test**: "Does this feel crafted or generated?"

### Icon Transformation Example
```
Recording indicator:
Before: Harsh red circle (triggers anxiety)
After: Soft amber glow with breathing animation,
       rounded form suggesting presence not surveillance,
       warm not warning
```

---

## Template Quick Reference

| Template | Aspect Ratio | Dimensions | Use Case |
|----------|--------------|------------|----------|
| `hero-banner` | 16:9 | 2560x1440 | Landing page hero |
| `og-card` | 1.91:1 | 1200x630 | Social/OG sharing |
| `twitter-card` | 2:1 | 1200x600 | Twitter/X cards |
| `icon-sheet` | 1:1 | 1024x1024 | Developer icons |
| `feature-banner` | 3:1 | 1920x640 | Feature sections |
| `mobile-hero` | 9:16 | 750x1334 | Mobile-first contexts |
| `interview-banner` | 16:9 | 1920x1080 | Interview mode specific |
| `card-background` | 4:3 | 800x600 | Card/tile backgrounds |

---

## Prompt Engineering Reference

### Core Style Elements (applied to all templates)

```
soft golden ambient light, subtle paper texture,
muted warm earth tones, artisanal crafted quality,
atmospheric depth, layered elements
```

### Standard Suffix

```
--style raw --no people faces text
```

### Custom Prompt Pattern

When creating custom prompts, combine:
1. **Subject**: What you're depicting
2. **Atmosphere**: `atmospheric`, `soft golden ambient light`
3. **Texture**: `subtle paper texture`, `layered elements`
4. **Colors**: `warm earth tones`, `amber`, `deep charcoal`
5. **Quality**: `artisanal crafted quality`
6. **Composition**: `CENTER-WEIGHTED` for banners, `HIGH CONTRAST` for icons
7. **Flags**: `--style raw --no people faces text`

---

## Responsive Image Sizing Reference

### Hero Banners

| Breakpoint | Dimensions | Aspect Ratio | Midjourney |
|------------|------------|--------------|------------|
| Desktop HD | 1920 x 1080 px | 16:9 | `--ar 16:9` |
| Desktop Retina | 2560 x 1440 px | 16:9 | `--ar 16:9` then upscale |
| Tablet | 1024 x 768 px | 4:3 | `--ar 4:3` |
| Mobile | 750 x 1334 px | 9:16 | `--ar 9:16` |

**Safe Zone Strategy**: Generate at 2560x1440, keep focal point in center 50%. Crop for each breakpoint from center.

### OG / Social Cards

| Platform | Dimensions | Aspect Ratio | Midjourney |
|----------|------------|--------------|------------|
| Universal (Facebook, LinkedIn, Slack) | 1200 x 630 px | 1.91:1 | `--ar 1.91:1` |
| Twitter/X | 1200 x 600 px | 2:1 | `--ar 2:1` |
| Square (Instagram, fallback) | 1200 x 1200 px | 1:1 | `--ar 1:1` |

### Feature/Section Banners

| Type | Dimensions | Aspect Ratio | Midjourney |
|------|------------|--------------|------------|
| Wide header | 1920 x 640 px | 3:1 | `--ar 3:1` |
| Card background | 800 x 600 px | 4:3 | `--ar 4:3` |
| Narrow strip | 1920 x 400 px | ~5:1 | `--ar 5:1` |

### Icons (Multi-Resolution Export)

| Size | Use Case |
|------|----------|
| 16 x 16 px | Favicon, tiny UI |
| 24 x 24 px | Inline icons |
| 32 x 32 px | Standard UI icons |
| 48 x 48 px | Feature icons |
| 64 x 64 px | Card icons |
| 128 x 128 px | Large displays |
| 192 x 192 px | Android Chrome |
| 512 x 512 px | PWA, app stores |
| SVG | Preferred for all scalable contexts |

### File Format & Size Guidelines

| Asset Type | Format | Max Size | Notes |
|------------|--------|----------|-------|
| Hero images | WebP (PNG/JPEG fallback) | 500 KB | Use compression |
| Icons | SVG preferred, PNG for raster | 50 KB | Export at 2x for retina |
| OG images | JPEG (photos) / PNG (graphics) | 300 KB | Test with social debuggers |
| Backgrounds | WebP with fallback | 200 KB | Consider CSS gradients as alternative |

---

## Anti-Patterns

**Never do these:**

| Anti-Pattern | Why | Instead |
|--------------|-----|---------|
| Pure flat colors | Feels sterile | Add subtle gradients or noise |
| Generic SaaS illustrations | Floating people, abstract shapes feel hollow | Use atmospheric, textured imagery |
| Harsh contrast | Creates anxiety | Soften edges, use intermediate tones |
| Sterile perfection | Lacks humanity | Add subtle texture, hand-crafted feel |
| Pure black backgrounds | Too heavy, lifeless | Warm darks (deep charcoal) |
| Frantic animations | Increases stress | Slow, breathing movements |
| Sharp geometric icons | Cold, corporate | Organic curves, rounded terminals |
| Bright warning colors | Triggers anxiety | Warm amber, soft indicators |

---

## Workflow Examples

### Example 1: Generate a Hero Banner

```bash
python scripts/generate_image.py hero-banner
```

Then view the result:
```bash
ls -lt generated-assets/ | head -5
```

Use Read tool on the generated image file to view it.

### Example 2: Custom Feature Artwork

```bash
python scripts/generate_image.py custom \
  --prompt "abstract visualization of real-time code analysis, neural pathways of understanding" \
  --ar 16:9 \
  --output-prefix "code-analysis"
```

### Example 3: Review Existing Assets

```bash
# List all generated assets
ls -la generated-assets/

# Find specific types
ls generated-assets/ | grep hero
ls generated-assets/ | grep interview
```

---

## Quick Reference Card

```
ATMOSPHERE: Calm Confidence
FEELING: "The deep breath before you speak"

COLORS: Warm darks + golden amber
TEXTURE: Paper grain, soft noise
DEPTH: Layered, soft shadows
MOTION: Breathing, slow pulses
ICONS: Monoline, organic curves, rounded terminals

KEY PROMPT ELEMENTS:
- atmospheric
- soft golden ambient light
- subtle paper texture
- warm earth tones
- artisanal crafted quality
- --style raw
- --no people faces text

SCRIPT: python scripts/generate_image.py <template>
OUTPUT: generated-assets/
```

---

## References

- APIframe documentation: https://apiframe.pro/docs
- Midjourney documentation: https://docs.midjourney.com/
