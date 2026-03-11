# Customizing Your Brand Identity

The Art Design Plugin uses YAML configuration files for brand identity and review criteria. You can customize these to match your own visual identity without modifying any code.

## Configuration Files

| File | Purpose |
|------|---------|
| `config/brand-guidelines.yaml` | Defines colors, textures, feelings, prompt modifiers |
| `config/review-criteria.yaml` | Defines review checklist and failure handling |

## Customizing Brand Guidelines

Edit `config/brand-guidelines.yaml`:

### Change the Brand Name and Tagline

```yaml
name: "Your Brand Name"
tagline: "Your brand's essence in one line"
```

### Define Target Feelings

What emotions should your visuals evoke?

```yaml
feelings:
  target:
    - "Energetic"
    - "Bold"
    - "Modern"
    - "Innovative"
    - "Built with taste"
  avoid:
    - "Boring"
    - "Dated"
    - "Corporate"
```

### Customize Color Palette

```yaml
colors:
  primary:
    description: "Your primary brand color"
    hex: "#FF6B35"
  accent:
    description: "Secondary accent"
    primary: "electric blue"
    hex: "#0066FF"
  background:
    description: "Background color family"
    examples:
      - "pure white"
      - "light gray"
```

### Define Textures

What textures should appear in your images?

```yaml
textures:
  required:
    - "smooth gradients"
    - "subtle glow effects"
    - "clean edges"
  avoid:
    - "rough textures"
    - "grain overlays"
    - "paper effects"
```

### Customize Prompt Modifiers

These are appended to all generation prompts:

```yaml
prompt_style:
  base: "vibrant colors, modern aesthetic, clean lines, bold composition"
  suffix_midjourney: "--style raw --no clutter text"
  suffix_nano_banana: ""
```

## Customizing Review Criteria

Edit `config/review-criteria.yaml`:

### Change Failure Behavior

```yaml
on_failure:
  # Options: suggest_refinement, auto_regenerate, warn_only
  action: "auto_regenerate"
  max_regeneration_attempts: 3
  refinement_prompt_template: "Fix: {failed_criteria}"
```

| Action | Behavior |
|--------|----------|
| `suggest_refinement` | Returns suggestions for manual improvement |
| `auto_regenerate` | Automatically attempts to fix using NBP edit |
| `warn_only` | Shows issues but takes no action |

### Adjust Passing Threshold

```yaml
passing_threshold: 80  # Require 80% score to pass
```

### Modify Category Weights

```yaml
categories:
  color_warmth:
    weight: 0.5  # Lower importance
  texture:
    weight: 1.0  # Higher importance
```

### Disable Categories

```yaml
categories:
  texture:
    enabled: false  # Skip texture checks entirely
```

### Add Custom Criteria

```yaml
custom_criteria:
  - name: "Brand Logo Visibility"
    check: "Company logo is visible in corner"
    weight: 0.9
    required: true

  - name: "Color Accessibility"
    check: "Sufficient contrast for accessibility (WCAG AA)"
    weight: 0.7
    required: false

  - name: "No Competitor Colors"
    check: "Does not prominently feature competitor brand colors"
    weight: 0.8
    required: true
```

## Example: Minimalist Tech Brand

```yaml
# config/brand-guidelines.yaml
name: "Clean Tech"
tagline: "Simplicity is the ultimate sophistication"

feelings:
  target:
    - "Clean"
    - "Professional"
    - "Innovative"
    - "Trustworthy"
  avoid:
    - "Cluttered"
    - "Playful"
    - "Vintage"
    - "Organic"

colors:
  primary:
    description: "Pure white backgrounds"
    hex: "#FFFFFF"
  accent:
    description: "Tech blue accent"
    hex: "#0066FF"
  text:
    description: "Near-black for readability"
    hex: "#1A1A1A"

textures:
  required:
    - "smooth gradients"
    - "subtle shadows"
    - "clean edges"
  avoid:
    - "paper grain"
    - "noise overlays"
    - "organic textures"

prompt_style:
  base: "minimalist design, clean white space, subtle blue accents, professional tech aesthetic, crisp edges"
  suffix_midjourney: "--style raw --no clutter decoration ornaments"
  suffix_nano_banana: ""
```

## Example: Playful Creative Brand

```yaml
# config/brand-guidelines.yaml
name: "Creative Spark"
tagline: "Where imagination meets innovation"

feelings:
  target:
    - "Playful"
    - "Creative"
    - "Energetic"
    - "Inspiring"
  avoid:
    - "Corporate"
    - "Sterile"
    - "Boring"
    - "Formal"

colors:
  primary:
    description: "Vibrant gradient backgrounds"
    examples:
      - "purple to pink"
      - "blue to cyan"
  accent:
    description: "Bright highlight colors"
    primary: "yellow"
    secondary: "orange"

textures:
  required:
    - "dynamic gradients"
    - "geometric patterns"
    - "bold shapes"
  avoid:
    - "flat solid colors"
    - "muted tones"

prompt_style:
  base: "vibrant colorful, dynamic composition, geometric shapes, energetic mood, creative and playful"
  suffix_midjourney: "--style raw --no boring plain simple"
  suffix_nano_banana: ""
```

## Auto-Regeneration Flow

When `on_failure.action` is set to `auto_regenerate`:

1. Image fails one or more criteria
2. System builds refinement prompt from failed checks
3. Calls Nano Banana Pro edit with the original image
4. Reviews the new image
5. Repeats up to `max_regeneration_attempts` times
6. If still failing, falls back to `suggest_refinement`

## Tips

1. **Start with defaults**: Modify the existing Calm Confidence config gradually
2. **Test incrementally**: Generate a few images after each change
3. **Be specific**: Detailed prompt modifiers produce better results
4. **Balance weights**: Don't make all criteria weight 1.0
5. **Document changes**: Keep notes on what works for your brand
