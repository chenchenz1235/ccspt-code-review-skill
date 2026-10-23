# DeepSeek Harness adapter

This directory contains manual integration notes only; no harness runtime or installation has been validated by this repository.

Use the canonical directories under `plugins/ccspt-code-review-skill/skills/`:

- `ccspt-code-review`: toolkit entrypoint; requires the two sibling specialties.
- `ccspt-motor-parameter-review`: motor parameter review, usable independently.
- `ccspt-thermostat-logic`: thermostat documentation and review, usable independently.

Configure these as custom skill sources only if the target harness supports them. When copying, preserve the three sibling directories so entrypoint links resolve. Keep this repository as the source of truth; do not copy project source files into the skill package. Motor parameter review runs its own version check. Updating an installed skill requires the user's choice.
