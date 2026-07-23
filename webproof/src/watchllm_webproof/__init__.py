"""Public API for the WatchLLM WebProof Python SDK."""

from .agent import VerifiableAgent
from .config import AggregationConfig, RouteConfig, WebProofConfig, load_config
from .exceptions import AgentClosedError, ConfigError, UnsupportedSchemeError, WebProofError

__all__ = [
    "AgentClosedError",
    "AggregationConfig",
    "ConfigError",
    "RouteConfig",
    "UnsupportedSchemeError",
    "VerifiableAgent",
    "WebProofConfig",
    "WebProofError",
    "load_config",
]

__version__ = "0.1.0"
