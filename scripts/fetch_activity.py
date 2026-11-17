#!/usr/bin/env python3
"""
fetch_activity.py
Fetches recent commits and public repository activity for Kekkan74's flagship projects.
Uses standard library urllib so it runs anywhere without external dependencies.
Saves balanced commit stream to data/activity.json.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

# Flagship portfolio repositories (excludes dotfiles, Top-Globales, and profile sync commits)
REPOSITORIES = [
    "data_voley",
    "CenterLock",
    "Sitecrack",
    "socket_pocket",
    "gen_effects",
    "PokeStat",
]


def fetch_recent_commits(username: str, output_file: str) -> None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GitHub-Activity-Fetcher",
        "Accept": "application/vnd.github.v3+json",
    }

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    per_repo_commits = {}
    print(f"[*] Fetching commit activity for user '{username}' across {len(REPOSITORIES)} flagship repositories...")

    for repo in REPOSITORIES:
        url = f"https://api.github.com/repos/{username}/{repo}/commits?per_page=5"
        per_repo_commits[repo] = []
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                commits_data = json.loads(resp.read().decode("utf-8"))
                for c in commits_data:
                    sha = c.get("sha", "")[:7]
                    commit_obj = c.get("commit", {})
                    author_obj = commit_obj.get("author", {})
                    raw_date = author_obj.get("date", "")
                    raw_msg = commit_obj.get("message", "").split("\n")[0].strip()

                    low_msg = raw_msg.lower()
                    if "merge" in low_msg:
                        event_type = "MERGE"
                    elif "feat" in low_msg or "add" in low_msg or "initial" in low_msg:
                        event_type = "FEAT"
                    elif "chore" in low_msg or "refresh" in low_msg:
                        event_type = "SYNC"
                    elif "fix" in low_msg or "patch" in low_msg:
                        event_type = "PATCH"
                    elif "docs" in low_msg:
                        event_type = "DOCS"
                    elif "config" in low_msg:
                        event_type = "CONFIG"
                    else:
                        event_type = "COMMIT"

                    per_repo_commits[repo].append(
                        {
                            "repo": repo,
                            "sha": sha,
                            "type": event_type,
                            "message": raw_msg,
                            "date": raw_date,
                            "url": f"https://github.com/{username}/{repo}/commit/{sha}",
                        }
                    )
        except urllib.error.HTTPError as e:
            print(f"[!] HTTP error fetching {repo}: {e.code}", file=sys.stderr)
        except Exception as e:
            print(f"[!] Error fetching {repo}: {e}", file=sys.stderr)

    # Showcase 1 latest commit from each flagship repository first, then fill up to 6
    selected_commits = []
    for repo in REPOSITORIES:
        if per_repo_commits.get(repo):
            selected_commits.append(per_repo_commits[repo][0])

    if len(selected_commits) < 6:
        for repo in REPOSITORIES:
            for extra in per_repo_commits.get(repo, [])[1:]:
                if len(selected_commits) < 6:
                    selected_commits.append(extra)

    # Sort chronologically descending
    selected_commits.sort(key=lambda x: x["date"], reverse=True)

    if not selected_commits and os.path.exists(output_file):
        print("[!] No new commits fetched. Keeping existing data.")
        return

    result = {
        "username": username,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_repos_tracked": len(REPOSITORIES),
        "recent_commits": selected_commits[:6],
    }

    out_dir = os.path.dirname(output_file)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[+] Successfully saved {len(result['recent_commits'])} flagship commits to {output_file}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user = sys.argv[1] if len(sys.argv) > 1 else "Kekkan74"
    out_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(base_dir, "data", "activity.json")
    fetch_recent_commits(user, out_file)
