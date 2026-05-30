# Legacy Code

This directory contains deprecated code from the old multi-agent competitive DAG architecture.

## Deprecated Components

- `planner.py` - Old `WorkflowPlanner` that generated parallel DAG with 3 research + 3 write + 1 review nodes
- `executor.py` - Old `LangGraphExecutor` that executed competitive multi-agent workflow

## Why Deprecated

The system has been refactored to use a **Pipeline + SkillPool** architecture:
- No more multi-agent competition
- No more winner selection by ReviewAgent
- Sequential pipeline execution with clear step dependencies
- Each step invokes a single Skill from the SkillPool

## Current Architecture

See `backend/pipeline/` for the new implementation:
- `PipelinePlanner` - Generates ordered pipeline steps
- `PipelineExecutor` - Executes steps sequentially
- `SkillPool` - Registry of reusable skills
- `skills/adapters/` - Individual skill implementations

## Migration Status

- ✅ `report_worker.py` switched to `PipelinePlanner` + `PipelineExecutor`
- ✅ All new reports use pipeline architecture
- ⚠️ Old agents still exist in `backend/agents/` for potential skill internal use
- ⚠️ `ReviewAgent` competition logic still present but not invoked by main flow

## Do Not Use

These files are kept for reference only. Do not import or use them in new code.
