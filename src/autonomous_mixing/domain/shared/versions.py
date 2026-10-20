"""Versioned references to specifications and implementations."""

from dataclasses import dataclass

from autonomous_mixing.domain.shared.invariants import require_text


@dataclass(frozen=True)
class VersionRef:
    """Exact identifier of a versioned specification or implementation; no implicit compatibility."""

    name: str
    version: str

    def __post_init__(self) -> None:
        require_text(self.name, "VersionRef.name")
        require_text(self.version, "VersionRef.version")
