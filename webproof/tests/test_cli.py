import json

import responses

from watchllm_webproof.cli import main


@responses.activate
def test_cli_exact_contract_with_json_config(tmp_path, capsys):
    config = tmp_path / "config.json"
    config.write_text('{"version":"1.0.0"}')
    responses.add(responses.GET, "https://example.com/", status=200)
    assert main(["verify-url", "https://example.com/", "--config", str(config)]) == 0
    proof = json.loads(capsys.readouterr().out)
    assert proof["leaf_count"] == 1
    assert proof["proof_type"] == "local_merkle_stub"


@responses.activate
def test_cli_config_is_optional(capsys):
    responses.add(responses.GET, "https://example.com/", status=200)
    assert main(["verify-url", "https://example.com/"]) == 0
    assert json.loads(capsys.readouterr().out)["attestation"] is False


def test_cli_sensible_error(capsys):
    assert main(["verify-url", "ftp://example.com/"]) == 1
    assert "HTTP and HTTPS only" in capsys.readouterr().err


def test_cli_cloud_is_explicit_and_requires_metadata_before_request(capsys):
    assert main(["verify-url", "https://example.com/", "--submit", "https://edge.test"]) == 1
    assert "--response-hash is required" in capsys.readouterr().err


@responses.activate
def test_cli_explicit_submission_outputs_only_public_status(monkeypatch, capsys):
    secret = "owner.do-not-print"
    monkeypatch.setenv("WATCHLLM_API_KEY", secret)
    responses.add(responses.GET, "https://example.com/", status=200)
    responses.add(
        responses.POST,
        "https://edge.test/proof",
        json={"verification_id": "00000000-0000-4000-8000-000000000001", "status": "queued"},
        status=202,
    )
    assert main([
        "verify-url", "https://example.com/", "--submit", "https://edge.test",
        "--response-hash", "22" * 32,
    ]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["status"] == "queued"
    assert secret not in captured.out + captured.err
