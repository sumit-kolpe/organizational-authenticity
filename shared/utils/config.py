"""Read and validate the small, versioned project configuration."""
from dataclasses import dataclass
from pathlib import Path

import yaml

from shared.utils.errors import ConfigurationError
from shared.utils.paths import CONFIG_PATH, PROJECT_ROOT


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _unique_mapping(loader, node):
    """Prevent a repeated setting from silently replacing an earlier value."""
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str):
            raise ConfigurationError("Configuration keys must be strings.")
        if key in result:
            raise ConfigurationError(f"Duplicate setting: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping
)


@dataclass(frozen=True)
class ResearchConfig:
    """Validated settings. Frozen instances prevent accidental reassignment."""

    project_name: str
    start_year: int
    end_year: int
    log_level: str

    @property
    def years(self) -> tuple[int, ...]:
        """Return the inclusive observation years, e.g. 2016 through 2024."""
        return tuple(range(self.start_year, self.end_year + 1))


def load_config(path: str | Path = CONFIG_PATH) -> ResearchConfig:
    """Read YAML and return validated settings; fail explicitly on bad input.

    Relative configuration paths are interpreted from the project root.
    This function performs no downloads and creates no output files.
    """
    source = Path(path)
    if not source.is_absolute():
        source = PROJECT_ROOT / source
    try:
        text = source.read_text(encoding="utf-8")
        raw = yaml.load(text, Loader=UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"Cannot read valid configuration at {source}: {exc}") from exc

    expected = {"project_name", "start_year", "end_year", "log_level"}
    if not isinstance(raw, dict):
        raise ConfigurationError("Configuration must be a YAML mapping of settings.")
    if set(raw) != expected:
        missing = sorted(expected - set(raw))
        extra = sorted(set(raw) - expected)
        raise ConfigurationError(f"Incorrect configuration keys; missing={missing}, extra={extra}")
    if not isinstance(raw["project_name"], str) or not raw["project_name"].strip():
        raise ConfigurationError("project_name must be a nonempty string.")
    # Exact type checks reject booleans, which Python otherwise treats as integers.
    for key in ("start_year", "end_year"):
        if type(raw[key]) is not int or not 1 <= raw[key] <= 9999:
            raise ConfigurationError(f"{key} must be an integer between 1 and 9999.")
    if raw["start_year"] > raw["end_year"]:
        raise ConfigurationError("start_year must not exceed end_year.")
    levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    if raw["log_level"] not in levels:
        raise ConfigurationError(f"log_level must be one of {levels}.")
    return ResearchConfig(**raw)
