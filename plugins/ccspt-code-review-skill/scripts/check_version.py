#!/usr/bin/env python3
"""Compare the installed plugin version with the version on GitHub main."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

DEFAULT_URL = (
    "https://raw.githubusercontent.com/chenchenz1235/"
    "ccspt-code-review-skill/main/plugins/ccspt-code-review-skill/VERSION"
)
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")


def read_local(path: Path) -> str:
    value = path.read_text(encoding="utf-8").strip()
    if not VERSION_RE.fullmatch(value):
        raise ValueError(f"invalid local version: {value!r}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args()

    local_path = Path(__file__).resolve().parent.parent / "VERSION"
    result = {
        "current_version": None,
        "latest_version": None,
        "update_available": None,
        "status": "unavailable",
    }

    try:
        current = read_local(local_path)
        result["current_version"] = current
        request = Request(args.remote_url, headers={"User-Agent": "ccspt-code-review-skill"})
        with urlopen(request, timeout=args.timeout) as response:
            latest = response.read().decode("utf-8").strip()
        if not VERSION_RE.fullmatch(latest):
            raise ValueError(f"invalid remote version: {latest!r}")
        result.update(
            latest_version=latest,
            update_available=current != latest,
            status="ok",
        )
    except (OSError, URLError, UnicodeError, ValueError) as exc:
        result["error"] = str(exc)

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
