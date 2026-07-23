"""Public exception hierarchy for watchllm-webproof."""


class WebProofError(Exception):
    """Base class for SDK errors."""


class ConfigError(WebProofError, ValueError):
    """Raised when configuration is missing, duplicate, or invalid."""


class UnsupportedSchemeError(WebProofError, ValueError):
    """Raised when a URL does not use HTTP or HTTPS."""


class AgentClosedError(WebProofError, RuntimeError):
    """Raised when a closed agent is used for another request."""
