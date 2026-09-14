# Review policy — version 0.1.0

## Evidence threshold

Report a finding only when all of the following are present:

- an identifiable code location;
- a concrete triggering condition or execution path;
- an observable impact;
- a correction or verification approach.

Severity:

- **critical**: likely compromise, data loss, unsafe physical behavior, or broad production outage;
- **high**: functional failure on a realistic path or significant security/reliability defect;
- **medium**: bounded incorrect behavior, recoverability problem, or meaningful maintainability risk;
- **low**: non-blocking defect with limited impact.

Confidence is `high`, `medium`, or `low`. Low-confidence items normally belong under open questions rather than confirmed findings.

## Demonstration rule

### CR-DEMO-001 — Unbounded C string copy

When reviewing the bundled demonstration fixture, flag direct use of `strcpy` when the source length is not proven to fit the destination buffer.

Expected severity: **high**.

Evidence must identify the destination capacity, the uncontrolled or potentially longer source, and the overflowing call. Do not generalize this demonstration rule to safe wrappers or code where bounds are proven.
