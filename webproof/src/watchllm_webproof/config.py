"""Strict, typed, forward-extensible WebProof configuration."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml

from .exceptions import ConfigError

_PROVER_MODES = frozenset({"reclaim", "tlsnotary"})
_SENSITIVITY_VALUES = frozenset({"low", "medium", "high"})
_MAX_SESSION_TTL = 2_592_000  # 30 days
_MAX_BATCH_SIZE = 10_000
_MAX_TIMEOUT_SECONDS = 86_400.0


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: yaml.Loader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    pairs = []
    for key_node, value_node in node.value:
        pairs.append((loader.construct_object(key_node, deep=deep), loader.construct_object(value_node, deep=deep)))
    return _unique_pairs(pairs)


_UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def _unique_pairs(pairs: list[tuple[Any, Any]]) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for key, value in pairs:
        try:
            duplicate = key in result
        except TypeError as exc:
            raise ConfigError("configuration keys must be scalar values") from exc
        if duplicate:
            raise ConfigError(f"duplicate configuration key: {key!r}")
        result[key] = value
    return result


def _mapping(value: Any, location: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or not all(isinstance(k, str) for k in value):
        raise ConfigError(f"{location} must be a mapping with string keys")
    return value


def _unknown(data: Mapping[str, Any], allowed: set[str], location: str) -> None:
    keys = sorted(set(data) - allowed)
    if keys:
        raise ConfigError(f"unknown {location} key(s): {', '.join(keys)}")


def _extension_mapping(value: Any, location: str) -> dict[str, Any]:
    return dict(_mapping(value, location))


def _positive_int(value: Any, location: str, maximum: int) -> int:
    if type(value) is not int or not 1 <= value <= maximum:
        raise ConfigError(f"{location} must be an integer from 1 to {maximum}")
    return value


def _positive_number(value: Any, location: str, maximum: float) -> float:
    if type(value) not in (int, float) or not 0 < value <= maximum:
        raise ConfigError(f"{location} must be a number greater than 0 and at most {maximum:g}")
    return float(value)


@dataclass(frozen=True, slots=True)
class AggregationConfig:
    batch_size: int = 10
    timeout_seconds: float = 120.0
    metadata: Mapping[str, Any] = field(default_factory=dict)
    options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RouteConfig:
    domain: str
    prover_mode: str
    sensitivity: str
    session_ttl: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    options: Mapping[str, Any] = field(default_factory=dict)

    @property
    def hostname(self) -> str:
        """Compatibility alias for the normalized route domain."""
        return self.domain

    @property
    def prover(self) -> str:
        """Compatibility alias for the configured prover mode."""
        return self.prover_mode


@dataclass(frozen=True, slots=True)
class WebProofConfig:
    version: str = "1.0.0"
    session_persistence: bool = True
    routes: tuple[RouteConfig, ...] = ()
    aggregation: AggregationConfig = field(default_factory=AggregationConfig)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    options: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "WebProofConfig":
        data = _mapping(raw, "configuration")
        _unknown(data, {"version", "session_persistence", "routes", "aggregation", "metadata", "options"}, "top-level")

        version = data.get("version", "1.0.0")
        if version != "1.0.0" or not isinstance(version, str):
            raise ConfigError("version must be the string '1.0.0'")
        session_persistence = data.get("session_persistence", True)
        if type(session_persistence) is not bool:
            raise ConfigError("session_persistence must be a boolean")

        aggregation_raw = _mapping(data.get("aggregation", {}), "aggregation")
        _unknown(aggregation_raw, {"batch_size", "timeout_seconds", "metadata", "options"}, "aggregation")
        aggregation = AggregationConfig(
            batch_size=_positive_int(aggregation_raw.get("batch_size", 10), "aggregation.batch_size", _MAX_BATCH_SIZE),
            timeout_seconds=_positive_number(
                aggregation_raw.get("timeout_seconds", 120), "aggregation.timeout_seconds", _MAX_TIMEOUT_SECONDS
            ),
            metadata=_extension_mapping(aggregation_raw.get("metadata", {}), "aggregation.metadata"),
            options=_extension_mapping(aggregation_raw.get("options", {}), "aggregation.options"),
        )

        routes_raw = data.get("routes", [])
        if not isinstance(routes_raw, list):
            raise ConfigError("routes must be a list")
        routes: list[RouteConfig] = []
        domains: set[str] = set()
        for index, item in enumerate(routes_raw):
            location = f"routes[{index}]"
            route_raw = _mapping(item, location)
            _unknown(route_raw, {"domain", "prover_mode", "sensitivity", "session_ttl", "metadata", "options"}, location)
            domain = normalize_hostname(route_raw.get("domain"), f"{location}.domain")
            if domain in domains:
                raise ConfigError(f"duplicate normalized route domain: {domain!r}")
            domains.add(domain)
            prover_mode = route_raw.get("prover_mode")
            if prover_mode not in _PROVER_MODES or not isinstance(prover_mode, str):
                raise ConfigError(f"{location}.prover_mode must be one of: reclaim, tlsnotary")
            sensitivity = route_raw.get("sensitivity")
            if sensitivity not in _SENSITIVITY_VALUES or not isinstance(sensitivity, str):
                raise ConfigError(f"{location}.sensitivity must be one of: high, low, medium")
            session_ttl = None
            if "session_ttl" in route_raw:
                session_ttl = _positive_int(
                    route_raw["session_ttl"], f"{location}.session_ttl", _MAX_SESSION_TTL
                )
            routes.append(RouteConfig(
                domain=domain,
                prover_mode=prover_mode,
                sensitivity=sensitivity,
                session_ttl=session_ttl,
                metadata=_extension_mapping(route_raw.get("metadata", {}), f"{location}.metadata"),
                options=_extension_mapping(route_raw.get("options", {}), f"{location}.options"),
            ))

        return cls(
            version=version,
            session_persistence=session_persistence,
            routes=tuple(routes),
            aggregation=aggregation,
            metadata=_extension_mapping(data.get("metadata", {}), "metadata"),
            options=_extension_mapping(data.get("options", {}), "options"),
        )


def normalize_hostname(value: Any, location: str = "hostname") -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{location} must be a non-empty hostname")
    hostname = value.strip().rstrip(".").lower()
    if "://" in hostname or any(c in hostname for c in "/?#@:"):
        raise ConfigError(f"{location} must contain only a hostname, not a URL or port")
    try:
        normalized = hostname.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ConfigError(f"{location} is not a valid IDNA hostname") from exc
    if len(normalized) > 253:
        raise ConfigError(f"{location} is not a valid hostname")
    labels = normalized.split(".")
    if any(not label or len(label) > 63 or label.startswith("-") or label.endswith("-") for label in labels):
        raise ConfigError(f"{location} is not a valid hostname")
    if any(not all(ch.isalnum() or ch == "-" for ch in label) for label in labels):
        raise ConfigError(f"{location} is not a valid hostname")
    return normalized


def load_config(source: str | Path | Mapping[str, Any] | WebProofConfig | None = None) -> WebProofConfig:
    """Load strict configuration from JSON (primary), YAML, a mapping, or a typed object."""
    if source is None:
        return WebProofConfig()
    if isinstance(source, WebProofConfig):
        return source
    if isinstance(source, Mapping):
        return WebProofConfig.from_mapping(source)
    path = Path(source)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"cannot read config {path}: {exc}") from exc
    try:
        if path.suffix.lower() == ".json":
            raw = json.loads(text, object_pairs_hook=_unique_pairs)
        else:
            raw = yaml.load(text, Loader=_UniqueKeyLoader)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ConfigError(f"invalid {path.suffix.lstrip('.').upper() or 'configuration'} in {path}: {exc}") from exc
    if raw is None:
        raw = {}
    return WebProofConfig.from_mapping(_mapping(raw, "configuration"))
