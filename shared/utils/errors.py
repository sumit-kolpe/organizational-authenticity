"""Errors callers can identify without inspecting error-message text."""


class ProjectError(Exception):
    """Base class for expected project failures."""


class ConfigurationError(ProjectError):
    """A configuration file is missing, unreadable or invalid."""
