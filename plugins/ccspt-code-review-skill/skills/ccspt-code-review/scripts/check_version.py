#!/usr/bin/env python3
"""Compare the installed version with GitHub without exposing credentials."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = (
    "https://api.github.com/repos/chenchenz1235/ccspt-code-review-skill/"
    "contents/plugins/ccspt-code-review-skill/skills/"
    "ccspt-code-review/VERSION?ref=main"
)
RAW_URL = (
    "https://raw.githubusercontent.com/chenchenz1235/"
    "ccspt-code-review-skill/main/plugins/ccspt-code-review-skill/"
    "skills/ccspt-code-review/VERSION"
)
VERSION_RE = re.compile(r"^[0-9]+\\.[0-9]+\\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")


def validate(value: str, source: str) -> str:
    value = value.strip()
    if not VERSION_RE.fullmatch(value):
        raise ValueError(f"invalid {source} version: {value!r}")
    return value


def fetch_with_token(url: str, token: str, timeout: float) -> str:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "ccspt-code-review-skill",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return base64.b64decode(payload["content"]).decode("utf-8")


def fetch_with_gh(timeout: float) -> str:
    completed = subprocess.run(
        [
            "gh",
            "api",
            "--method",
            "GET",
            "repos/chenchenz1235/ccspt-code-review-skill/contents/"
            "plugins/ccspt-code-review-skill/skills/ccspt-code-review/VERSION",
            "-f",
            "ref=main",
            "--jq",
            ".content",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    encoded = completed.stdout.replace("\\n", "").strip()
    return base64.b64decode(encoded).decode("utf-8")


def fetch_public(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": "ccspt-code-review-skill"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=4.0)
    args = parser.parse_args()

    local_path = Path(__file__).resolve().parent.parent / "VERSION"
    result = {
        "current_version": None,
        "latest_version": None,
        "update_available": None,
        "status": "unavailable",
        "method": None,
    }

    try:
        current = validate(local_path.read_text(encoding="utf-8"), "local")
        result["current_version"] = current

        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if token:
            remote = fetch_with_token(API_URL, token, args.timeout)
            result["method"] = "github-api-token"
        elif shutil.which("gh"):
            remote = fetch_with_gh(args.timeout)
            result["method"] = "github-cli"
        else:
            remote = fetch_public(RAW_URL, args.timeout)
            result["method"] = "public-raw"

        latest = validate(remote, "remote")
        result.update(
            latest_version=latest,
            update_available=current != latest,
            status="ok",
        )
    except (
        OSError,
        HTTPError,
        URLError,
        UnicodeError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ) as exc:
        result["error"] = (
            f"{type(exc).__name__}: {exc}. "
            "For a private repository, use an authenticated GitHub connector, "
            "an authenticated gh CLI, or GH_TOKEN/GITHUB_TOKEN."
        )

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
