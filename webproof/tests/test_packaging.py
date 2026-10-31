import shutil
import subprocess
import sys
from pathlib import Path


def test_unbuilt_source_tree_import_fails_closed_without_python_crypto_fallback(tmp_path):
    package = Path(__file__).parents[1] / "src" / "watchllm_webproof"
    isolated_source = tmp_path / "source"
    shutil.copytree(package, isolated_source / "watchllm_webproof", ignore=shutil.ignore_patterns("_native*", "__pycache__"))
    script = (
        "import sys; "
        f"sys.path.insert(0, {str(isolated_source)!r}); "
        "import watchllm_webproof"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", script],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert "requires its Rust native extension" in result.stderr
    assert "No cryptographic fallback is used" in result.stderr
