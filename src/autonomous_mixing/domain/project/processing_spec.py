"""Explicit numerical and encoding settings for bounded offline gain/full-mix processing.

A ``ProcessingSpec`` names how processing must be computed and encoded; it performs nothing.
Equality of recorded specifications establishes recorded configuration consistency only:
evidence citing a specification stays an adapter claim until the adapter is implemented and
tested. Processor identity is separate from this configuration. Experiment provenance still needs
Python, dependency and code/build versions and actual processing evidence. A stable operation
order does not promise bitwise-identical results in every environment, and no global registry
prevents one ``VersionRef`` from being reused inconsistently across separate records or runs.
"""

from dataclasses import dataclass
from enum import Enum

from autonomous_mixing.domain.shared import VersionRef, require_instance


class NumericalPrecision(Enum):
    FLOAT64 = "float64"  # all calculations in IEEE-754 double precision


class GainRule(Enum):
    DB_AMPLITUDE = "db_amplitude"  # multiplier 10 ** (gain_db / 20) applied to the fixed-input samples


class SummationOrder(Enum):
    """Evaluation order of the mix sum; ``SummingPolicy`` names the combination operation itself."""

    RECIPE_SEQUENTIAL = "recipe_sequential"  # zero accumulator, then add each stem in recipe order


class LevelPolicy(Enum):
    PRESERVE = "preserve"  # no clipping, normalization, limiting or automatic level correction


class OutputContainer(Enum):
    WAV = "wav"


class SampleEncoding(Enum):
    """Encoded sample format; a later file adapter maps it to its library's actual subtype."""

    FLOAT64 = "float64"  # 64-bit floating-point samples; no integer PCM conversion or dither


@dataclass(frozen=True)
class ProcessingSpec:
    """Complete, explicitly versioned processing configuration. Every field is required; no defaults."""

    reference: VersionRef
    precision: NumericalPrecision
    gain_rule: GainRule
    summation_order: SummationOrder
    level_policy: LevelPolicy
    output_container: OutputContainer
    sample_encoding: SampleEncoding

    def __post_init__(self) -> None:
        require_instance(self.reference, VersionRef, "ProcessingSpec.reference")
        require_instance(self.precision, NumericalPrecision, "ProcessingSpec.precision")
        require_instance(self.gain_rule, GainRule, "ProcessingSpec.gain_rule")
        require_instance(self.summation_order, SummationOrder, "ProcessingSpec.summation_order")
        require_instance(self.level_policy, LevelPolicy, "ProcessingSpec.level_policy")
        require_instance(self.output_container, OutputContainer, "ProcessingSpec.output_container")
        require_instance(self.sample_encoding, SampleEncoding, "ProcessingSpec.sample_encoding")
