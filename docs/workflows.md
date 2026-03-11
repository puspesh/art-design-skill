# Image Generation Workflows

The Art Design Plugin supports flexible workflows for generating, editing, and refining images.

## Workflow 1: Direct Generation

Generate images directly using a single engine.

```bash
# Using Midjourney (default)
python scripts/generate_image.py hero-banner

# Using Nano Banana Pro
python scripts/generate_image.py hero-banner --engine nbp --resolution 4K

# Custom prompt with art direction
python scripts/generate_image.py custom --prompt "developer workspace" --ar 16:9
```

## Workflow 2: Pipeline Refinement

Generate with one engine, then refine with another. This is the recommended workflow for:
- Adding textures or patterns
- Applying brand styling
- Adding logos or watermarks
- Enhancing details

```bash
# Basic pipeline: Midjourney -> Nano Banana Pro refinement
python scripts/generate_image.py hero-banner \
  --pipeline nbp \
  --refine-prompt "add subtle paper grain texture and warm golden light overlay"

# With 4K output resolution
python scripts/generate_image.py hero-banner \
  --pipeline nbp \
  --refine-prompt "add brand watermark in bottom right, enhance atmospheric depth" \
  --resolution 4K

# Feature banner with refinement
python scripts/generate_image.py feature-banner --feature "AI Interview" \
  --pipeline nbp \
  --refine-prompt "add geometric pattern overlay matching brand guidelines"
```

### Pipeline Behavior

1. **Generation Phase**: Creates image with primary engine (Midjourney by default)
2. **Intermediate Save**: Saves `{template}_intermediate_{timestamp}.png`
3. **Refinement Phase**: Passes image to Nano Banana Pro with refine-prompt
4. **Final Save**: Saves refined `{template}_{timestamp}.png`

If pipeline fails, you still have the intermediate result.

## Workflow 3: Multi-Step Editing

For complex edits, chain multiple edit commands:

```bash
# Step 1: Generate base image
python scripts/generate_image.py hero-banner -o step1

# Step 2: Add texture
python scripts/generate_image.py edit \
  --input generated-assets/step1_*.png \
  --prompt "add subtle paper grain texture throughout" \
  -o step2

# Step 3: Add brand elements
python scripts/generate_image.py edit \
  --input generated-assets/step2_*.png \
  --prompt "add warm golden light from top-left corner, brand logo watermark bottom-right" \
  -o final
```

## Workflow 4: Style Transfer

Use Midjourney style references for initial generation, then refine:

```bash
# Generate with style reference
python scripts/generate_image.py hero-banner \
  --sref https://example.com/brand-style.jpg \
  --sw 200 \
  --pipeline nbp \
  --refine-prompt "enhance details, add atmospheric fog"
```

## Workflow 5: Review and Auto-Refinement

Use the image-reviewer agent with auto-regeneration:

1. Configure `config/review-criteria.yaml`:
```yaml
on_failure:
  action: "auto_regenerate"
  max_regeneration_attempts: 2
  refinement_prompt_template: "Fix these issues: {failed_criteria}. Add brand-consistent textures and warmth."
```

2. Generate and review:
```bash
# Generate
python scripts/generate_image.py hero-banner

# The reviewer will automatically refine if criteria fail
```

## Common Refinement Prompts

### Texture Addition
```
"add subtle paper grain texture, soft noise overlay, atmospheric depth"
```

### Brand Styling
```
"apply warm golden color grading, add soft vignette, brand-consistent warmth"
```

### Logo/Watermark
```
"add [brand name] watermark in bottom-right corner, 10% opacity, white"
```

### Detail Enhancement
```
"enhance fine details, increase sharpness, add subtle highlights"
```

### Atmospheric Effects
```
"add atmospheric fog in background, depth of field effect, cinematic lighting"
```

## Output Files

| Stage | Filename Pattern | Contents |
|-------|------------------|----------|
| Initial | `{template}_{timestamp}_*.png` | Raw generation |
| Intermediate | `{template}_intermediate_{timestamp}_*.png` | Pre-refinement (pipeline) |
| Final | `{template}_{timestamp}_*.png` | After refinement |
| Edit | `edit_{timestamp}_*.png` | After edit command |

## Tips

1. **Save intermediate results**: Use `-o prefix` to track versions
2. **Iterate quickly**: Use `--no-download` to preview URLs first
3. **Combine references**: Mix `--sref` with pipeline for consistent style
4. **Review often**: Use the image-reviewer agent to catch issues early
