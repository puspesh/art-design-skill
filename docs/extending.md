# Extending the Art Design Plugin

This plugin is designed to be extended with additional skills, engines, and customizations.

## Adding Custom Skills

### Step 1: Create Skill Directory

Create a new directory under `skills/`:

```
skills/my-custom-skill/
└── SKILL.md
```

### Step 2: Define Your Skill

Create `SKILL.md` with frontmatter:

```markdown
---
name: my-custom-skill
description: What your skill does
version: 1.0.0
author: your-name
---

# My Custom Skill

## Trigger Conditions

This skill activates when...

## Solution Overview

Describe what the skill does and how to use it.
```

### Step 3: Use Existing Infrastructure

Your skill can use the existing image generation infrastructure:

```bash
# Generate with templates
python scripts/generate_image.py hero-banner

# Use custom prompts
python scripts/generate_image.py custom --prompt "your prompt" --ar 16:9

# Edit images
python scripts/generate_image.py edit --input image.png --prompt "edit instruction"
```

### Step 4: Access Configuration

Read brand guidelines in your skill:

```markdown
Read the brand configuration from `config/brand-guidelines.yaml` to understand
the current visual identity before generating assets.
```

## Adding Custom Engines

### Step 1: Create Engine File

Create a new engine in `scripts/engines/`:

```python
# scripts/engines/my_engine.py

from .base import BaseEngine, GenerationRequest, GenerationResult

class MyEngine(BaseEngine):
    """Custom image generation engine."""

    ENDPOINT = "https://api.example.com/generate"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": api_key,
        }

    @property
    def name(self) -> str:
        return "my-engine"

    @property
    def supports_editing(self) -> bool:
        return True  # or False

    def submit(self, request: GenerationRequest) -> str:
        # Implement API submission
        # Return task_id
        pass

    def fetch(self, task_id: str) -> GenerationResult:
        # Implement result fetching
        pass

    def build_prompt(self, request: GenerationRequest) -> str:
        # Build engine-specific prompt
        pass
```

### Step 2: Register Engine

Add to `scripts/engines/__init__.py`:

```python
from .my_engine import MyEngine

ENGINE_ALIASES = {
    # ... existing
    "my-engine": "my-engine",
    "me": "my-engine",  # short alias
}

ENGINE_CLASSES = {
    # ... existing
    "my-engine": MyEngine,
}
```

### Step 3: Use Your Engine

```bash
python scripts/generate_image.py hero-banner --engine my-engine
```

## Adding Custom Templates

### Step 1: Edit Templates

Add to `scripts/generate_image.py` in the `TEMPLATES` dict:

```python
TEMPLATES = {
    # ... existing templates
    "my-template": {
        "description": "My custom template (1920x1080)",
        "aspect_ratio": "16:9",
        "prompt": f"""
your custom prompt here, {STYLE_BASE},
additional styling instructions,
{STYLE_SUFFIX}
""",
    },
}
```

### Step 2: Use Your Template

```bash
python scripts/generate_image.py my-template
```

## Using the Plugin Namespace

When installed, skills are accessible as:
- `/art-design-skill:art-direction-visual-identity`
- `/art-design-skill:my-custom-skill`

## Adding Custom Agents

### Step 1: Create Agent File

Create in `agents/`:

```markdown
---
name: my-agent
description: What this agent does
tools: [Read, Bash, WebFetch]
---

# My Agent

You are a specialized agent that...

## Your Task

1. Step one
2. Step two
3. Step three
```

### Step 2: Reference in Manifest

The agent is auto-discovered from the `agents/` directory.

## Best Practices

1. **Follow naming conventions**: Use kebab-case for skill and agent names
2. **Document thoroughly**: Include trigger conditions and examples
3. **Respect brand guidelines**: Read config files before generating
4. **Handle errors gracefully**: Provide helpful error messages
5. **Version your changes**: Update CHANGELOG.md

## Example: Social Media Skill

```markdown
---
name: social-media-assets
description: Generate optimized assets for social media platforms
version: 1.0.0
---

# Social Media Assets Skill

## Trigger Conditions

Activates when generating assets for:
- Twitter/X posts
- LinkedIn posts
- Instagram stories
- Facebook posts

## Solution Overview

### Generate Twitter Card

\`\`\`bash
python scripts/generate_image.py twitter-card
\`\`\`

### Generate Instagram Story

\`\`\`bash
python scripts/generate_image.py custom --prompt "your content" --ar 9:16
\`\`\`
```
