"""Canonical exception hierarchy for Caligula. All pipeline errors must use these."""


class CaligulaError(Exception):
    """Base exception for all Caligula errors."""


class CaligulaDataError(CaligulaError):
    """Raised when source data is missing, malformed, or fails validation."""


class CaligulaExtractionError(CaligulaError):
    """Raised when AI extraction or EDGAR parsing fails."""


class CaligulaPointInTimeError(CaligulaError):
    """Raised when look-ahead bias or future data leakage is detected."""


class CaligulaScoringError(CaligulaError):
    """Raised during normalization, composite scoring, or ranking failures."""


class CaligulaBacktestError(CaligulaError):
    """Raised during backtest execution, holdings, or return calculation."""


class CaligulaValuationError(CaligulaError):
    """Raised during DCF, TV bucket logic, or cost of capital calculations."""
