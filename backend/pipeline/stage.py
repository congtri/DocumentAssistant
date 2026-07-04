"""Base stage interface for pipeline processing."""

from abc import ABC, abstractmethod

from backend.pipeline.context import PipelineContext


class Stage(ABC):
    """A single processing stage in the pipeline."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable stage name."""
        ...

    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute the stage, transforming the context."""
        ...
