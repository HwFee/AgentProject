class PipelineError(Exception):
    pass


class SkillNotFoundError(PipelineError):
    def __init__(self, skill_id: str):
        self.skill_id = skill_id
        super().__init__(f"Skill not found: {skill_id}")


class StepExecutionError(PipelineError):
    def __init__(self, step_id: str, original_error: Exception):
        self.step_id = step_id
        self.original_error = original_error
        super().__init__(f"Step '{step_id}' failed: {original_error}")


class PipelineAbortedError(PipelineError):
    def __init__(self, step_id: str, reason: str):
        self.step_id = step_id
        super().__init__(f"Pipeline aborted at step '{step_id}': {reason}")
