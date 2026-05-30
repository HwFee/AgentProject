# Pipeline + SkillPool Architecture

## Overview

The report generation system uses a **Pipeline + SkillPool** architecture instead of
multi-agent competitive DAG.

```
PipelinePlanner
  -> PipelinePlan (ordered steps)
  -> PipelineExecutor
    -> SkillPool.get(skill_id) -> SkillAdapter.execute()
    -> PipelineContext (carries artifacts)
    -> StepRun tracking (via AgentNode table)
  -> Final artifacts (report, PDF, DOCX)
```

## Architecture Comparison

### Old Architecture (Deprecated)

```
WorkflowPlanner
  -> Parallel DAG (3 research + 3 write + 1 review)
  -> LangGraphExecutor
    -> ResearchAgent x3 (parallel)
    -> WriteAgent x3 (parallel, competitive)
    -> ReviewAgent (selects winner)
  -> Final report (winner)
```

**Problems:**
- Multi-agent competition wastes resources
- ReviewAgent winner selection is subjective
- Complex DAG execution logic
- Hard to debug and extend

### New Architecture (Current)

```
PipelinePlanner
  -> Sequential Pipeline (8 steps)
  -> PipelineExecutor
    -> SkillPool.get(skill_id)
    -> SkillAdapter.execute(context, step)
    -> PipelineContext.artifacts
  -> Final report + quality check + exports
```

**Benefits:**
- Clear step-by-step execution
- Each step has defined input/output
- Easy to add/remove/modify steps
- Better error handling and retry support
- Quality check without competition

## Domain Model

```
ReportTask owns one PipelineRun.
PipelineRun contains ordered StepRuns.
StepRun invokes one Skill.
Skill produces output into PipelineContext.
PipelineContext carries all intermediate artifacts.
```

## Key Concepts

- **Pipeline**: An ordered execution plan for report generation.
- **PipelineStep**: A single step in the pipeline, bound to a skill.
- **Skill**: A reusable capability (research, analysis, writing, export).
- **SkillAdapter**: Concrete implementation of a skill.
- **PipelineRun**: A single execution record of a pipeline.
- **StepRun**: Execution record of a single step.
- **Artifact**: Intermediate or final output (research_notes, draft_report, etc.).
- **PipelineContext**: Shared state container carrying all artifacts between steps.

## Pipeline Steps (Default)

1. `requirement.intake` - Normalize user requirement
2. `planning.outline` - Generate report outline
3. `research.collect` - Web research and attachment summarization
4. `data.analyze` - Data analysis on attachments (conditional)
5. `writing.draft_report` - Generate first draft
6. `writing.de_ai_polish` - De-AI polish for human-like writing
7. `review.quality_check` - Quality check against requirements
8. `export.report_files` - Export to DOCX/PDF

## DB Compatibility

StepRun records are mapped to the existing `AgentNode` table:
- `AgentNode.node_id` = step.id
- `AgentNode.agent_type` = step.skill_id
- `AgentNode.output_data` = SkillResult.output (truncated to 2000 chars)
- `AgentNode.status` = step status
- `AgentNode.token_usage` = skill token usage

## External SKILL.md Compatibility

The system supports loading external skills from `skills/` directory:
- `SkillPackageLoader` discovers SKILL.md files
- `PromptSkillAdapter` wraps them as LLM prompt skills
- Registered in SkillPool with `prompt.{name}` skill_id
- Scripts are NOT executed (security)

## API Endpoints

### Pipeline-specific

- `GET /api/reports/{id}/pipeline` - Get pipeline execution details with steps
- `GET /api/reports/{id}/steps` - Get step list
- `GET /api/reports/{id}/artifacts` - Get step artifacts
- `GET /api/skills` - List all registered skills

### Legacy (still supported)

- `GET /api/reports/{id}/dag` - Returns nodes + edges (pipeline steps as linear chain)
- `GET /api/reports/{id}/status` - Returns task status + nodes

## Legacy Code

The old multi-agent architecture has been moved to `backend/legacy/`:
- `legacy/planner.py` - WorkflowPlanner (deprecated)
- `legacy/executor.py` - LangGraphExecutor (deprecated)

Old agents still exist in `backend/agents/` but are not used by the main flow.

## Future Plans

- Migrate to dedicated `pipeline_runs`, `step_runs`, `artifacts` tables
- Add step retry support
- Add dynamic pipeline generation (LLM-based step selection)
- Add parallel step execution for independent steps
- Add step-level progress streaming

## File Structure

```
backend/
  pipeline/
    __init__.py
    types.py          # PipelineStep, PipelinePlan, PipelineContext, SkillResult
    planner.py        # PipelinePlanner
    executor.py       # PipelineExecutor
    skill_pool.py     # SkillPool
    errors.py         # Custom exceptions

  skills/
    base.py           # SkillAdapter protocol
    package.py        # SkillPackage dataclass
    loader.py         # SkillPackageLoader
    prompt_adapter.py # PromptSkillAdapter
    adapters/
      requirement_intake.py
      outline_plan.py
      research_collect.py
      data_analyze.py
      report_draft.py
      de_ai_polish.py
      quality_review.py
      export_report.py

  legacy/
    planner.py        # Deprecated WorkflowPlanner
    executor.py       # Deprecated LangGraphExecutor
    README.md

  workers/
    report_worker.py  # Uses PipelinePlanner + PipelineExecutor
```
