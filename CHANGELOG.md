# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-02-04

### Added
- **Nano Banana Pro engine support** (Gemini image model via APIframe)
- **Image editing capabilities** via `edit` command
- **Pipeline workflows** - Generate with Midjourney, refine with Nano Banana Pro
- **Resolution control** for Nano Banana Pro (1K, 2K, 4K)
- **Engine abstraction layer** for extensibility
- **Customizable brand identity** via `config/brand-guidelines.yaml`
- **Customizable review criteria** via `config/review-criteria.yaml`
- **Image reviewer agent** with configurable checklist
- **Auto-regeneration on review failure** (configurable)
- Comprehensive workflow documentation
- Extension guide for developers

### Changed
- Converted to marketplace-compatible plugin structure
- Updated manifest to `plugin.json` format (Anthropic best practices)
- Added hooks configuration for portability
- Brand guidelines now externalized and user-overridable
- Improved documentation structure

### Removed
- Local settings file (replaced by portable hooks)
- Old manifest.json format

## [2.0.0] - 2025-01-19

### Added
- **Image reference support** (`--sref`, `--cref`, `--image-url`)
- Style weight control (`--sw`)
- Character weight control (`--cw`)
- Image weight control (`--iw`)
- Interview banner modes (human-human, bot-human, bot-bot)

### Changed
- Updated skill documentation with reference examples
- Improved prompt templates

## [1.0.0] - 2025-01-01

### Added
- Initial release
- Midjourney integration via APIframe
- Pre-configured art direction templates:
  - hero-banner
  - og-card
  - twitter-card
  - icon-sheet
  - feature-banner
  - mobile-hero
  - interview-banner
  - card-background
- "Calm Confidence" visual identity system
- Local asset management
- Custom and raw prompt modes
