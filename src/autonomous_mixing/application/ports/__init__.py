"""Compatibility package: re-exports the application port Protocols from their owning components.

Deprecated import location kept for existing callers; new code imports ``AudioAnalyzer`` from
``autonomous_mixing.application.observation``, ``DecisionController`` from
``autonomous_mixing.application.decision`` and ``AudioProcessor`` from
``autonomous_mixing.application.execution``. Concrete implementations live outside the application layer.
The submodules are themselves re-export shims; nothing here defines a port.
"""

from autonomous_mixing.application.ports.analysis import AudioAnalyzer
from autonomous_mixing.application.ports.decision import DecisionController
from autonomous_mixing.application.ports.processing import AudioProcessor

__all__ = ["AudioAnalyzer", "DecisionController", "AudioProcessor"]
