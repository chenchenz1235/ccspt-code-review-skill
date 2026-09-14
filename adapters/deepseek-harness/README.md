# DeepSeek Harness adapter

The canonical skill is:

`plugins/ccspt-code-review-skill/skills/ccspt-code-review`

For the first proof of concept, configure that directory as a custom skill source or copy it into the project-level DeepSeek Harness skill directory. Keep the GitHub repository as the source of truth. Run `scripts/check_version.py` before review; update the clone only after explicit confirmation.

DeepSeek Harness is still in developer preview, so this adapter intentionally contains no harness-specific runtime code.
