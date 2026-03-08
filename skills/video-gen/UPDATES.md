# Video Gen Updates

Structured changelog for AI agents. Read this to determine what changed and whether updates are safe to apply.

## 2026-03-08

### new-files

| File | Description |
|------|-------------|
| `SKILL.md` | Skill definition with light mode + project mode documentation |
| `scripts/generate.py` | Light mode: fal.ai multi-model video generation |
| `scripts/preview.py` | Quick preview wrapper (generate + open in viewer) |
| `scripts/project_init.py` | Project mode: initialize project structure |
| `scripts/project_state.py` | Project mode: state management + status display |
| `scripts/decompose.py` | Project mode: LLM prompt for story decomposition |
| `scripts/keyframe.py` | Project mode: generate keyframe images per scene |
| `scripts/clip.py` | Project mode: generate video clips per scene |
| `scripts/assemble.py` | Project mode: ffmpeg assembly of clips to final MP4 |
| `scripts/character_sheet.py` | Project mode: multi-view character image sheets |
| `references/models.md` | Model catalog: all models, endpoints, capabilities |
| `references/model-kling.md` | Kling 3.0 reference card |
| `references/model-veo.md` | Veo 3.1 reference card |
| `references/model-sora.md` | Sora 2 reference card |
| `references/model-ltx.md` | LTX-2.3 reference card |
| `references/model-wan.md` | Wan 2.5/2.6 reference card |
| `references/model-hailuo.md` | Hailuo-02 reference card |
| `references/fal-api.md` | fal.ai queue API reference |
| `references/pricing.md` | Cost per model per second |
| `references/prompt-guide.md` | Video prompt engineering guide |
| `references/camera-vocabulary.md` | Camera movement/angle vocabulary |
| `references/style-keywords.md` | Style keyword reference |
| `references/story-schema.md` | JSON schema for story.json |
| `references/scene-schema.md` | JSON schema for scene objects |
| `references/shot-schema.md` | JSON schema for shot objects |
| `references/character-schema.md` | JSON schema for character objects |
| `references/consistency-guide.md` | Visual consistency across scenes |
| `references/cost-reference.md` | Cost estimation for project mode |
| `references/model-selection.md` | Project mode model selection guide |
| `references/prompt-assembly.md` | How prompts are assembled for scenes |
| `prompts/enhance.md` | Universal prompt enhancement template |
| `prompts/enhance-cinematic.md` | Cinematic/film style enhancement |
| `prompts/enhance-animated.md` | Animation/stylized enhancement |
| `prompts/decompose.md` | Story decomposition system prompt |

### changed-files
(none -- initial release)

### removed-files
(none -- initial release)

### breaking-changes
(none -- initial release)

### migration-notes
- Initial release. Merged from legacy video-gen + story-gen skills.
- Credential management changed from legacy vault CLI flow to `FAL_KEY` environment variable.
- Image-gen dependency uses 3-tier resolution: IMAGE_GEN_SCRIPT env var > peer auto-discovery > actionable error.
- produce.py (legacy batch pipeline) excluded from v1.0.0 -- will be added in v1.1.0.
