---
name: ccspt-code-review
description: Review selected code, a change set, or a feature implementation using the CCSpt evidence-based process, engineer clarification loop, and standardized report. Use when a user asks for code review, change review, defect review, or review-report generation.
license: UNLICENSED
compatibility: Requires repository read access. Network access is optional and used only to check for a newer skill version.
---

# CCSpt Code Review

Produce a reproducible review with evidence, not a generic style critique.

## Pre-review update gate

Complete this gate before opening, reading, or analyzing any requested source file, diff, or review target.

1. Read `VERSION` and record it as `skill_version`.
2. Check the latest `plugins/ccspt-code-review-skill/skills/ccspt-code-review/VERSION` on the private GitHub repository. Prefer an authenticated GitHub connector when the harness provides one; otherwise run `scripts/check_version.py`.
3. If the installed version is current, continue directly to the review.
4. If a newer version exists, stop before processing the review target and tell the user both versions: `发现新版本：当前 <installed>，最新 <latest>。是否先更新？` Wait for the user's choice.
5. If the user chooses to update, use the harness's supported Skill or plugin update mechanism, verify the installed version, and only then begin processing the review target. If updating fails or no updater is available, explain the problem and ask whether to continue with the installed version.
6. If the user declines or postpones the update, continue with the installed version.
7. Never install an update without the user's choice. If the update check is unavailable, do not block the review; record the unavailable status and continue.

## Start

1. Identify the requested review scope. If no scope is stated, review the current change set; if that is unavailable, ask for the target files or feature.
2. Accept engineer-provided intent, constraints, known risks, and test evidence at any time. Treat them as context, not proof that the implementation is correct.

## Review

Read [review policy](references/review-policy.md) before reviewing. Inspect relevant implementation, callers, tests, configuration, and error paths. Use existing repository tools when they materially improve confidence.

Every reported finding must contain a concrete failure mode and code evidence. Do not report preferences, speculative risks without a plausible path, or issues outside the requested scope. Deduplicate findings.

For the bundled demonstration fixture, apply `CR-DEMO-001` from the review policy.

## Clarification

When missing engineer knowledge could change a finding, ask a focused question and mark the finding `needs-confirmation`. Incorporate the answer into the final report. Never upload or email engineer content without explicit user approval for that specific destination.

## Output

Use [the report template](assets/report-template.md). Include:

- skill version, local ruleset hash when available, harness/model if known, reviewed revision or file set, and update-check result;
- findings ordered by severity;
- exact file and line evidence;
- engineer responses and resulting status;
- checks run, checks not run, and remaining uncertainty.

If feedback is requested, produce a sanitized feedback package using [the feedback schema](references/feedback-schema.md). Creating the package does not authorize sending it.
