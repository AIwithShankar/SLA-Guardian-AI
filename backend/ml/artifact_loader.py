"""Checksum-gated loading of the local Phase 4 research artifact."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

TRUSTED_ARTIFACT_DIR = (
    Path(__file__).resolve().parents[2] / "ml" / "artifacts"
)
DEFAULT_METADATA_PATH = TRUSTED_ARTIFACT_DIR / "model_metadata.json"


class ArtifactTrustError(RuntimeError):
    """Raised when an artifact fails the local trust or compatibility checks."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_artifact_checksum(
    artifact_path: Path,
    expected_sha256: str,
) -> None:
    """Raise unless the local artifact hash exactly matches metadata."""

    actual_sha256 = _sha256(artifact_path)
    if actual_sha256.lower() != expected_sha256.lower():
        raise ArtifactTrustError(
            "Artifact SHA-256 does not match the trusted metadata: "
            f"expected {expected_sha256}, got {actual_sha256}"
        )


def _require_trusted_path(artifact_path: Path, metadata_path: Path) -> None:
    trusted_dir = TRUSTED_ARTIFACT_DIR.resolve()
    if artifact_path.resolve().parent != trusted_dir:
        raise ArtifactTrustError(
            "Only artifacts in the repository's trusted ml/artifacts directory "
            "may be loaded"
        )
    if metadata_path.resolve().parent != trusted_dir:
        raise ArtifactTrustError(
            "Model metadata must come from the repository's trusted "
            "ml/artifacts directory"
        )


def _require_runtime_dependencies(dependency_versions: dict[str, str]) -> None:
    module_to_distribution = {
        "joblib": "joblib",
        "numpy": "numpy",
        "pandas": "pandas",
        "sklearn": "scikit-learn",
        "lightgbm": "lightgbm",
    }
    missing = [
        module
        for module in module_to_distribution
        if importlib.util.find_spec(module) is None
    ]
    if missing:
        raise ArtifactTrustError(
            "Model runtime dependencies are unavailable: " + ", ".join(missing)
        )
    training_python = dependency_versions.get("python")
    if not isinstance(training_python, str):
        raise ArtifactTrustError("Metadata does not declare the training Python version")
    training_major_minor = ".".join(training_python.split(".")[:2])
    running_major_minor = f"{sys.version_info.major}.{sys.version_info.minor}"
    if running_major_minor != training_major_minor:
        raise ArtifactTrustError(
            "Python major/minor version is incompatible: "
            f"artifact used {training_major_minor}, running {running_major_minor}"
        )

    mismatches = []
    for module, distribution in module_to_distribution.items():
        expected = dependency_versions.get(distribution)
        if expected is None:
            raise ArtifactTrustError(
                f"Metadata does not declare the {distribution} version"
            )
        try:
            installed = version(distribution)
        except PackageNotFoundError:
            installed = None
        if installed != expected:
            mismatches.append(f"{distribution}={installed!r} (expected {expected})")
    if mismatches:
        raise ArtifactTrustError(
            "Model runtime dependency versions are incompatible: "
            + ", ".join(mismatches)
        )


def load_trusted_model(
    artifact_path: Path | None = None,
    metadata_path: Path = DEFAULT_METADATA_PATH,
) -> Any:
    """Verify and load only the checked-in, metadata-declared model artifact."""

    artifact_path = (
        TRUSTED_ARTIFACT_DIR / "breach_classifier.joblib"
        if artifact_path is None
        else Path(artifact_path)
    )
    metadata_path = Path(metadata_path)
    _require_trusted_path(artifact_path, metadata_path)

    if not artifact_path.is_file() or not metadata_path.is_file():
        raise ArtifactTrustError("Trusted model artifact or metadata is missing")

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ArtifactTrustError("Trusted model metadata cannot be read") from error

    if metadata.get("artifact_filename") != artifact_path.name:
        raise ArtifactTrustError("Artifact filename does not match metadata")
    expected_sha256 = metadata.get("artifact_sha256")
    if not isinstance(expected_sha256, str) or not expected_sha256:
        raise ArtifactTrustError("Metadata does not declare an artifact checksum")
    if metadata.get("provisional_research_only") is not True:
        raise ArtifactTrustError("Only research-only artifacts may be loaded")

    verify_artifact_checksum(artifact_path, expected_sha256)
    dependency_versions = metadata.get("dependency_versions")
    if not isinstance(dependency_versions, dict):
        raise ArtifactTrustError("Metadata does not declare runtime dependencies")
    _require_runtime_dependencies(dependency_versions)

    import joblib

    return joblib.load(artifact_path)
