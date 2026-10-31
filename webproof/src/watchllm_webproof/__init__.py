"""Public API for the WatchLLM WebProof Python SDK."""

from .agent import VerifiableAgent
from .cloud import CloudClient, CloudResult, build_edge_envelope
from .config import AggregationConfig, RouteConfig, WebProofConfig, load_config
from .exceptions import AgentClosedError, CloudSubmissionError, ConfigError, UnsupportedSchemeError, WebProofError

__all__ = [
    "AgentClosedError",
    "AggregationConfig",
    "CloudClient",
    "CloudResult",
    "CloudSubmissionError",
    "ConfigError",
    "RouteConfig",
    "UnsupportedSchemeError",
    "VerifiableAgent",
    "WebProofConfig",
    "WebProofError",
    "build_edge_envelope",
    "load_config",
]

__version__ = "0.2.0"
