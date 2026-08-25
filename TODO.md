# TODO

- `requirements.txt` is dead: not referenced by Makefile or docs, and `pyproject.toml`
  already has the same dependencies (this repo migrated to `uv` like its siblings but
  never removed the old file). Delete it.
- ROADMAP.md's "Where we are today" section describes a pre-rewrite state that no
  longer exists: it says the pipeline is `scripts/captions_pipeline.py` producing
  platform captions + SEO tags via `agents/*.yaml` (platform). That file doesn't exist
  anymore — commits `5dd7b77` ("implement ROADMAP Phase 1+2, extract artist memory
  instead of captions") and `b713677` ("remove platform captions, keep examples dir
  empty") already did the rewrite the roadmap proposes. The gap analysis table needs
  updating to reflect the current `extract_pipeline.py` / memory-first architecture,
  or a future read will re-diagnose a problem that's already fixed.
- No CI, despite solid coverage (9 test files across agent_config, extract_pipeline,
  memory_schema, pipeline_utils, task_config, prompt rules, tags/ollama options).
