"""Run with: python -m shared.check_setup (from the repository root)."""
import sys

from shared.utils.config import load_config
from shared.utils.errors import ConfigurationError
from shared.utils.logging_utils import setup_logging
from shared.utils.paths import LOG_DIR, PROJECT_ROOT


def main() -> int:
    """Check configuration and logging; return a nonzero status on failure."""
    try:
        config = load_config()
        logger = setup_logging(config.log_level)
    except (ConfigurationError, OSError) as exc:
        # Configuration/log startup failures must still be visible without a logger.
        print(f"SETUP FAILED: {exc}", file=sys.stderr)
        return 1

    logger.info("Setup check started")
    logger.info("Project: %s", config.project_name)
    logger.info("Project root: %s", PROJECT_ROOT)
    logger.info("Years: %s (%s annual time points)", config.years, len(config.years))
    logger.info("Log file: %s", LOG_DIR / "research.log")
    logger.info("Setup check passed; no research data were collected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
