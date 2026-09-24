import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError


def lookup(owner, repository, opener=urlopen):
    for value in (owner, repository):
        if not re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_.-]{0,99}", value):
            raise ValueError("Use a GitHub owner and repository name, not a URL or path")
    config = json.loads((Path(__file__).resolve().parents[1] / "assets/config.json").read_text())
    url = f"https://api.github.com/repos/{owner}/{repository}"
    request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "sample-agent-skills"})
    with opener(request, timeout=config["timeout_seconds"]) as response:
        payload = json.load(response)
    return {
        "repository": payload["full_name"],
        "description": payload.get("description"),
        "stars": payload["stargazers_count"],
        "default_branch": payload["default_branch"],
        "source_url": url,
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("owner")
    parser.add_argument("repository")
    args = parser.parse_args()
    try:
        print(json.dumps(lookup(args.owner, args.repository)))
    except (URLError, OSError, ValueError, KeyError) as error:
        print(json.dumps({"error": str(error)}))
        raise SystemExit(1)
