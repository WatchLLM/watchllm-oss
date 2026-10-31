import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from watchllm_webproof.accumulator import LocalMerkleAccumulator, canonical_leaf

VECTORS = json.loads((Path(__file__).parent / "vectors" / "commitment-v1.json").read_text())


@pytest.mark.parametrize("vector", VECTORS["vectors"], ids=lambda vector: vector["name"])
def test_historical_python_contract_golden_vectors(vector):
    accumulator = LocalMerkleAccumulator()
    for record, expected in zip(vector["records"], vector["canonical"], strict=True):
        historical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        assert historical == expected.encode()
        assert bytes(canonical_leaf(record)) == historical
        accumulator.record(record)
    assert accumulator.proof("golden")["merkle_root"] == vector["merkle_root"]
    assert accumulator.proof("golden")["leaf_count"] == len(vector["records"])


def test_proof_contract_is_local_and_non_attesting():
    proof = LocalMerkleAccumulator().proof("session")
    assert proof == {
        "proof_type": "local_merkle_stub",
        "proof_version": "1.0.0",
        "attestation": False,
        "algorithm": "sha256-local-merkle-v1",
        "aggregation_enabled": True,
        "merkle_root": hashlib.sha256(b"").hexdigest(),
        "leaf_count": 0,
        "session_id": "session",
    }


def test_records_are_deeply_immutable_snapshots():
    record = {"nested": {"items": [1, 2]}, "ok": True}
    accumulator = LocalMerkleAccumulator()
    accumulator.record(record)
    original_root = accumulator.proof("x")["merkle_root"]
    record["nested"]["items"].append(3)
    snapshot = accumulator.records
    snapshot[0]["nested"]["items"].append(4)
    assert accumulator.records == ({"nested": {"items": [1, 2]}, "ok": True},)
    assert accumulator.proof("x")["merkle_root"] == original_root


@pytest.mark.parametrize("value", [1.5, float("nan"), float("inf"), {"set": {1}}, {1: "not a string key"}, {"bytes": b"no"}, {"object": object()}])
def test_rejects_values_outside_supported_commitment_contract(value):
    with pytest.raises((TypeError, ValueError), match="unsupported|keys must be strings"):
        LocalMerkleAccumulator().record(value if isinstance(value, dict) else {"value": value})


def test_arbitrary_precision_integers_cross_native_boundary_without_truncation():
    enormous = 10**500
    accumulator = LocalMerkleAccumulator()
    accumulator.record({"enormous": enormous, "negative": -enormous})
    expected = json.dumps({"enormous": enormous, "negative": -enormous}, sort_keys=True, separators=(",", ":")).encode()
    assert bytes(canonical_leaf({"negative": -enormous, "enormous": enormous})) == expected
    assert accumulator.records[0]["enormous"] == enormous


@pytest.mark.parametrize("kind", ["list", "dict", "mixed", "deep"])
def test_recursive_inputs_fail_without_crashing_native_process(kind):
    # A subprocess makes SIGSEGV a normal assertion failure instead of taking
    # down the complete test run. This executes the installed/built extension,
    # not a Python fallback.
    program = r'''
from watchllm_webproof.accumulator import LocalMerkleAccumulator, canonical_leaf
import importlib.util
import sys

spec = importlib.util.find_spec("watchllm_webproof._native")
if spec is None or not spec.origin or not spec.origin.endswith((".so", ".pyd")):
    raise AssertionError(f"not using a built native extension: {spec}")

kind = sys.argv[1]
if kind == "list":
    value = []
    value.append(value)
elif kind == "dict":
    value = {}
    value["self"] = value
elif kind == "mixed":
    value = []
    child = {"back": value}
    value.append(child)
else:
    value = None
    for _ in range(10_000):
        value = [value]

for operation in (canonical_leaf, lambda item: LocalMerkleAccumulator().record(item)):
    try:
        operation({"value": value})
    except ValueError as error:
        expected = "nesting exceeds" if kind == "deep" else "circular references"
        if expected not in str(error):
            raise AssertionError(str(error)) from error
    else:
        raise AssertionError("recursive input was accepted")
'''
    result = subprocess.run(
        [sys.executable, "-c", program, kind],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, (
        f"native subprocess exited {result.returncode}; "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )


def test_maximum_supported_depth_remains_deterministic():
    nested = None
    for _ in range(127):
        nested = [nested]
    record = {"value": nested}
    expected = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    assert bytes(canonical_leaf(record)) == expected


def test_rejects_lone_unicode_surrogates():
    with pytest.raises(ValueError, match="lone surrogates"):
        LocalMerkleAccumulator().record({"value": "\ud800"})


def test_concurrent_records_are_safe_and_complete():
    accumulator = LocalMerkleAccumulator()
    with ThreadPoolExecutor(max_workers=12) as executor:
        list(executor.map(lambda value: accumulator.record({"value": value}), range(500)))
    records = accumulator.records
    assert len(records) == 500
    assert {record["value"] for record in records} == set(range(500))
    assert accumulator.proof("concurrent")["leaf_count"] == 500
