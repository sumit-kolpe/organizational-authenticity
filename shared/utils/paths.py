"""Find paths from this module's location, not the terminal's directory."""
from pathlib import Path

# paths.py -> utils -> shared -> repository root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "research_config.yaml"
LOG_DIR = PROJECT_ROOT / "logs"


def project_path(*parts: str) -> Path:
    """Build a path inside the repository; do not create files or directories."""
    candidate = PROJECT_ROOT.joinpath(*parts).resolve()
    if not candidate.is_relative_to(PROJECT_ROOT):
        raise ValueError("Requested path is outside the project root.")
    return candidate
