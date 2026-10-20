"""Small synthetic tests; no external requests, company data or API calls."""
import contextlib
import io
import logging
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from shared.check_setup import main
from shared.utils.config import load_config
from shared.utils.errors import ConfigurationError
from shared.utils.logging_utils import setup_logging
from shared.utils.paths import PROJECT_ROOT, project_path

VALID = "project_name: demo\nstart_year: 2016\nend_year: 2024\nlog_level: INFO\n"


class InfrastructureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / "test.yaml"

    def read_config(self, text):
        self.config.write_text(text, encoding="utf-8")
        return load_config(self.config)

    def test_inclusive_years(self):
        self.assertEqual(self.read_config(VALID).years, tuple(range(2016, 2025)))

    def test_single_year(self):
        self.assertEqual(self.read_config(VALID.replace("2024", "2016")).years, (2016,))

    def test_invalid_configurations(self):
        invalid = [
            "", "[]", "start_year: [", VALID + "extra: 3\n",
            VALID + "start_year: 2017\n", VALID.replace("2016", "true"),
            VALID.replace("2016", '"2016"'), VALID.replace("2016", "2025"),
            VALID.replace("INFO", "LOUD"), VALID.replace("demo", '""'),
            VALID.replace("end_year: 2024\n", ""),
        ]
        for text in invalid:
            with self.subTest(text=text), self.assertRaises(ConfigurationError):
                self.read_config(text)

    def test_missing_file(self):
        with self.assertRaises(ConfigurationError):
            load_config(self.root / "missing.yaml")

    def test_default_scope(self):
        self.assertEqual(load_config().years, tuple(range(2016, 2025)))

    def test_paths_and_config_ignore_working_directory(self):
        with patch("os.getcwd", return_value=str(self.root)):
            self.assertEqual(project_path("config"), PROJECT_ROOT / "config")
            self.assertEqual(load_config("config/research_config.yaml").start_year, 2016)

    def test_outside_path_rejected(self):
        with self.assertRaises(ValueError):
            project_path("..", "outside")

    def test_logging_repeated_setup_and_levels(self):
        directory = self.root / "logs"
        with contextlib.redirect_stderr(io.StringIO()):
            logger = setup_logging("INFO", directory)
            logger = setup_logging("INFO", directory)
            try:
                logger.debug("hidden-debug")
                logger.info("one-visible-message")
                for handler in logger.handlers:
                    handler.flush()
                content = (directory / "research.log").read_text(encoding="utf-8")
                self.assertEqual(content.count("one-visible-message"), 1)
                self.assertNotIn("hidden-debug", content)
                self.assertIn("Z | INFO |", content)
            finally:
                for handler in list(logger.handlers):
                    logger.removeHandler(handler)
                    handler.close()

    def test_cli_reports_configuration_failure(self):
        stream = io.StringIO()
        with patch("shared.check_setup.load_config", side_effect=ConfigurationError("bad config")):
            with contextlib.redirect_stderr(stream):
                self.assertEqual(main(), 1)
        self.assertIn("SETUP FAILED", stream.getvalue())

    def test_invalid_logging_level(self):
        with self.assertRaises(ValueError):
            setup_logging("LOUD", self.root)


if __name__ == "__main__":
    unittest.main()
