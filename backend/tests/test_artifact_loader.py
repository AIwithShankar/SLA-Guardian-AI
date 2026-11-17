import hashlib
import json
from pathlib import Path

import pytest

from ml.artifact_loader import (
    ArtifactTrustError,
    TRUSTED_ARTIFACT_DIR,
    verify_artifact_checksum,
)


def test_model_artifact_checksum_matches_metadata() -> None:
    artifact = TRUSTED_ARTIFACT_DIR / "breach_classifier.joblib"
    metadata = json.loads(
        (TRUSTED_ARTIFACT_DIR / "model_metadata.json").read_text(
            encoding="utf-8"
        )
    )
    actual = hashlib.sha256(artifact.read_bytes()).hexdigest()

    assert actual == metadata["artifact_sha256"]


def test_checksum_mismatch_is_rejected(tmp_path: Path) -> None:
    artifact = tmp_path / "altered.joblib"
    artifact.write_bytes(b"not the trusted model")

    with pytest.raises(ArtifactTrustError, match="SHA-256"):
        verify_artifact_checksum(artifact, "0" * 64)


def test_loader_rejects_artifacts_outside_trusted_directory(
    tmp_path: Path,
) -> None:
    with pytest.raises(ArtifactTrustError, match="trusted ml/artifacts"):
        from ml.artifact_loader import load_trusted_model

        load_trusted_model(tmp_path / "uploaded.joblib")
