# CCSpt Code Review Skill

A cross-harness, versioned code-review workflow for Codex, Claude Code, and DeepSeek Harness.

Current version: **0.1.1**

## What this version proves

- One canonical `SKILL.md` is shared by multiple agent harnesses.
- Every report records the skill version and update status.
- The demo rule `CR-DEMO-001` detects unbounded C string copies such as `strcpy`.
- Engineer feedback is generated locally and is never uploaded or emailed without explicit approval.

## Repository layout

- `plugins/ccspt-code-review-skill/`: portable plugin and shared skill.
- `.agents/plugins/marketplace.json`: Codex repository marketplace.
- `.claude-plugin/marketplace.json`: Claude Code marketplace.
- `tests/demo-case/`: reproducible demonstration fixture.

## First test

Ask the agent to use **ccspt-code-review** to review `tests/demo-case/demo.c`.
The result should identify `CR-DEMO-001` and show the installed skill version.

## Update test

An installation that still has version `0.1.0` should discover version `0.1.1` on GitHub and report that an update is available. It must not install the update automatically during a review.

## Private-repository update checks

An authenticated GitHub connector is preferred. Command-line users can use an authenticated `gh` CLI or provide `GH_TOKEN`/`GITHUB_TOKEN` through their existing secret-management setup. The checker never prints the token. If no authenticated route is available, update status is reported as unavailable instead of claiming the installation is current.

This repository is private. Do not upload company source code, diffs, logs, credentials, or customer information as feedback.
