import json
from pathlib import Path

import pytest
import responses

from watchllm_webproof import CloudClient, CloudSubmissionError, VerifiableAgent, build_edge_envelope
from watchllm_webproof.accumulator import LocalMerkleAccumulator

UUID = "00000000-0000-4000-8000-000000000001"
HASH = "22" * 32
FIXTURE = Path(__file__).parents[1] / "edge" / "test" / "fixtures" / "python-envelope-v1.json"


def native_fixture_envelope():
    fixture = json.loads(FIXTURE.read_text())
    records = fixture.pop("_python_records")
    accumulator = LocalMerkleAccumulator()
    for record in records:
        accumulator.record(record)
    return build_edge_envelope(
        accumulator.records,
        accumulator.proof("python-edge-contract"),
        leaf_index=2,
        response_hash=HASH,
        observed_at=1_784_976_000_000,
        chain="base-sepolia",
    ), fixture


def test_python_generated_cross_boundary_fixture_is_current():
    if not FIXTURE.exists():
        # webproof/edge is proprietary and excluded from the OSS export, so the
        # committed edge fixture is not present there. Skip instead of failing.
        pytest.skip("edge fixture not available in this export")
    generated, fixture = native_fixture_envelope()
    assert generated == fixture
    assert json.loads(__import__("base64").b64decode(generated["proof_payload"]))["proof"]["leaf_count"] == 3


def test_envelope_matches_native_proof_and_rejects_semantic_mismatch():
    accumulator = LocalMerkleAccumulator()
    accumulator.record({"domain": "example.com", "path": "/x"})
    proof = accumulator.proof("session")
    envelope = build_edge_envelope(
        accumulator.records,
        proof,
        leaf_index=0,
        response_hash=HASH,
        observed_at=1_784_976_000_000,
    )
    assert envelope["leaf_hash"] == envelope["merkle_root"]
    assert envelope["merkle_path"] == []
    with pytest.raises(ValueError, match="leaf_count"):
        build_edge_envelope([], proof, leaf_index=0, response_hash=HASH, observed_at=1_784_976_000_000)


@responses.activate
def test_submit_status_and_bounded_poll_use_bearer_without_exposing_it():
    secret = "owner.super-secret-value"
    responses.add(
        responses.POST,
        "https://edge.test/proof",
        json={"verification_id": UUID, "status": "queued", "unexpected": secret},
        status=202,
    )
    responses.add(
        responses.GET,
        f"https://edge.test/proof/{UUID}",
        json={"verification_id": UUID, "status": "submitted"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"https://edge.test/proof/{UUID}",
        json={"verification_id": UUID, "status": "anchored"},
        status=200,
    )
    clock = [0.0]

    def sleep(seconds):
        clock[0] += seconds

    with CloudClient("https://edge.test", secret, sleep=sleep, monotonic=lambda: clock[0]) as client:
        submitted = client.submit({"envelope_version": "1"})
        result = client.poll(submitted.verification_id, timeout=10, initial_interval=1)
    assert result.status == "anchored"
    assert responses.calls[0].request.headers["Authorization"] == f"Bearer {secret}"
    assert secret not in repr(submitted)
    assert secret not in repr(result)


@responses.activate
def test_stored_only_status_is_honest_and_remains_nonterminal_for_polling():
    responses.add(
        responses.POST,
        "https://edge.test/proof",
        json={"verification_id": UUID, "status": "stored", "anchoring_mode": "disabled"},
        status=202,
    )
    with CloudClient("https://edge.test", "owner.secret") as client:
        result = client.submit({"envelope_version": "1"})
    assert result.status == "stored"
    assert result.data["anchoring_mode"] == "disabled"


def test_poll_returns_latest_stored_result_when_sleep_reaches_deadline():
    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {"verification_id": UUID, "status": "stored", "anchoring_mode": "disabled"}

    class Session:
        def __init__(self):
            self.calls = 0

        def request(self, *args, **kwargs):
            self.calls += 1
            return Response()

    clock = [0.0]
    session = Session()

    def sleep(seconds):
        clock[0] += seconds

    with CloudClient("https://edge.test", "owner.secret", session=session, sleep=sleep, monotonic=lambda: clock[0]) as client:
        result = client.poll(UUID, timeout=1, initial_interval=1, max_interval=1)
    assert result.status == "stored"
    assert result.data["anchoring_mode"] == "disabled"
    assert session.calls == 1


@responses.activate
def test_transport_and_http_errors_are_sanitized():
    secret = "owner.super-secret-value"
    responses.add(responses.POST, "https://edge.test/proof", body=f"bad {secret}", status=401)
    with CloudClient("https://edge.test", secret) as client:
        with pytest.raises(CloudSubmissionError) as caught:
            client.submit({})
    assert secret not in str(caught.value)


def test_local_agent_has_no_implicit_cloud_calls():
    with VerifiableAgent(session_id="local-only") as agent:
        assert agent.proof()["leaf_count"] == 0


@pytest.mark.parametrize("endpoint", ["http://edge.test", "https://user:password@edge.test", "https://edge.test?token=x"])
def test_cloud_endpoint_must_be_safe_https(endpoint):
    with pytest.raises(ValueError):
        CloudClient(endpoint, "owner.secret")
