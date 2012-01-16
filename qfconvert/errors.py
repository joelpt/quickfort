"""Basic exception classes."""


class AreaPlotterError(Exception):
    """Base class for areaplotter errors."""


class BlueprintError(Exception):
    """Base class for errors in the blueprint package."""


class FileError(Exception):
    """Base class for file parsing related errors."""


class LogError(Exception):
    """Base class for errors occurring within logger."""


class ParametersError(Exception):
    """Base class for errors related to command line parameters."""
