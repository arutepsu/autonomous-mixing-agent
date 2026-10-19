# ADR-008 — controlled defect injection into real stems (2026-10-15)
- Decision: controlled, parameterized defect injection into real musical stems from self-created projects is permitted for calibration and evaluation data. Artificially generated music (synthetic tracks or arrangements, including generated kick/bass material) is not scientific evaluation data and is not used for demonstrations. Synthetic numerical signals remain permitted for focused unit tests only.
- Clarifies: ADR-006 point 6 ("Generated audio is never a scientific evaluation dataset"). That point refers to artificially generated music, not to controlled modifications of real stems. ADR-006 otherwise remains in force.
- Source: researcher approval of Requirements Specification v1.0, 2026-10-15.
- Rationale: controlled injection yields documented, reproducible problem conditions in realistic musical material, as planned in `research/dataset-plan.md`; fully synthetic material would not represent the musical context the research questions address.
- Consequences:
  - Injection parameters and random seeds are recorded per variant; all variants of a source project stay in the same data split (requirements SR-02, FR-18).
  - Labels derived from injection state only that a defect was injected with given parameters, not that it is perceptually relevant (SR-07).
  - Injected faults are not automatically representative of real-world mixing problems; this remains a documented validity risk.
