"""Run from the project root: python -m shared.check_companies."""
from collections import Counter
import sys

from shared.utils.companies import load_companies, validate_assignment_sample
from shared.utils.config import load_config
from shared.utils.errors import ProjectError
from shared.utils.logging_utils import setup_logging


def main() -> int:
    """Validate metadata and report expected scope, not observed data coverage."""
    logger = None
    try:
        config = load_config()
        logger = setup_logging(config.log_level)
        companies = load_companies()
        validate_assignment_sample(companies)
    except (ProjectError, OSError) as exc:
        if logger is None:
            print(f"COMPANY CHECK FAILED: {exc}", file=sys.stderr)
        else:
            logger.error("COMPANY CHECK FAILED: %s", exc)
        return 1

    logger.info("Validated %s unique assignment companies", len(companies))
    for sector, count in sorted(Counter(row["sector"] for row in companies).items()):
        logger.info("%s: %s companies", sector, count)
    logger.info("Configured years: %s through %s (%s years)",
                config.start_year, config.end_year, len(config.years))
    logger.info("Target company-year observations: %s (not collected observations)",
                len(companies) * len(config.years))
    logger.info("Company metadata check passed; historical URLs remain unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
