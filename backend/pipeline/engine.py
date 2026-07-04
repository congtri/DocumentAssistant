"""Pipeline engine that executes stages sequentially."""

from backend.core.logger import logger
from backend.pipeline.context import PipelineContext
from backend.pipeline.stage import Stage


class PipelineEngine:
    """Executes a sequence of stages, passing context through each."""

    def __init__(self, stages: list[Stage] | None = None):
        self._stages: list[Stage] = stages or []

    def add_stage(self, stage: Stage) -> "PipelineEngine":
        self._stages.append(stage)
        return self

    def execute(self, context: PipelineContext | None = None) -> PipelineContext:
        context = context or PipelineContext()

        for stage in self._stages:
            logger.info(f"Pipeline stage: {stage.name}")
            try:
                context = stage.execute(context)
            except Exception as e:
                error_msg = f"Stage '{stage.name}' failed: {e}"
                logger.error(error_msg)
                context.add_error(error_msg)
                break

        return context
