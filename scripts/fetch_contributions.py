#!/usr/bin/env python3
"""
fetch_contributions.py
Fetches the public GitHub contribution graph for a user using BeautifulSoup and requests.
Zero tokens required. Saves parsed data to data/contributions.json.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

def fetch_contributions(username: str, output_file: str):
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html"
    }

    print(f"[*] Fetching public contribution graph for '{username}'...")
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[!] Error fetching contributions from GitHub: {e}", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(resp.text, "html.parser")

    # Map tooltips for contribution counts
    tooltip_map = {}
    for tt in soup.find_all("tool-tip"):
        for_id = tt.get("for")
        if for_id:
            tooltip_map[for_id] = tt.text.strip()

    days_data = []
    total_contributions = 0

    calendar_cells = soup.find_all(["td", "rect"], class_=lambda c: c and "ContributionCalendar-day" in c)
    if not calendar_cells:
        print("[!] No contribution days found. Check username or GitHub layout.", file=sys.stderr)
        sys.exit(1)

    for cell in calendar_cells:
        date_str = cell.get("data-date")
        if not date_str:
            continue

        level = int(cell.get("data-level", 0))
        cell_id = cell.get("id", "")
        tt_text = tooltip_map.get(cell_id, "")

        count = 0
        m = re.search(r"(\d+)\s+contribution", tt_text)
        if m:
            count = int(m.group(1))

        total_contributions += count

        # Compute weekday (Sunday = 0, Saturday = 6)
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = (dt.weekday() + 1) % 7

        days_data.append({
            "date": date_str,
            "level": level,
            "count": count,
            "weekday": weekday
        })

    # Sort chronologically
    days_data.sort(key=lambda d: d["date"])

    # Calculate streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    for day in days_data:
        if day["count"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0
    current_streak = temp_streak

    result = {
        "username": username,
        "total_contributions": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "days_count": len(days_data),
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "days": days_data
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"[+] Successfully saved {len(days_data)} days to {output_file}")
    print(f"    Total contributions: {total_contributions} | Longest streak: {longest_streak} days")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user = sys.argv[1] if len(sys.argv) > 1 else "Kekkan74"
    out_json = sys.argv[2] if len(sys.argv) > 2 else os.path.join(base_dir, "data", "contributions.json")
    fetch_contributions(user, out_json)
