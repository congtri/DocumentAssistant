"""Prompt template loader.

Loads Markdown templates and performs variable substitution.
"""

from pathlib import Path

from backend.core.logger import logger

TEMPLATES_DIR = Path(__file__).parent / "templates"


class PromptLoader:
    """Loads and caches prompt templates from Markdown files."""

    def __init__(self, templates_dir: Path | None = None):
        self._dir = templates_dir or TEMPLATES_DIR
        self._cache: dict[str, str] = {}

    def load(self, template_name: str, **variables: str) -> str:
        """Load a template and substitute variables.

        Variables in templates use {{variable_name}} syntax.
        """
        template = self._get_template(template_name)
        for key, value in variables.items():
            template = template.replace(f"{{{{{key}}}}}", value)
        return template

    def _get_template(self, name: str) -> str:
        if name in self._cache:
            return self._cache[name]

        path = self._dir / f"{name}.md"
        if not path.exists():
            logger.warning(f"Template not found: {path}")
            return ""

        content = path.read_text(encoding="utf-8").strip()
        self._cache[name] = content
        return content

    def clear_cache(self) -> None:
        self._cache.clear()


prompt_loader = PromptLoader()
