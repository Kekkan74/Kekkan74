#!/usr/bin/env python3
"""
render_commit_activity_svg.py
Renders an animated, SOC-styled terminal SVG displaying recent commit activity
and live telemetry across monitored repositories.
Zero tokens, 100% SVG + CSS, GitHub camo-compatible.
"""

import html
import json
import os
import sys
from datetime import datetime

def format_date(iso_str: str) -> str:
    """Converts 2026-10-28T04:57:41Z to 2026-10-28 04:57"""
    try:
        dt = datetime.strptime(iso_str.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_str[:16].replace("T", " ")

def render_commit_activity(activity_json_path: str, output_svg_path: str):
    if not os.path.exists(activity_json_path):
        print(f"[!] Activity JSON not found: {activity_json_path}", file=sys.stderr)
        sys.exit(1)

    with open(activity_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    commits = data.get("recent_commits", [])
    total_repos = data.get("total_repos_tracked", 4)
    updated_at = data.get("updated_at", "RECENT")

    svg_width = 860
    svg_height = 295

    # Badge color mappings
    badge_colors = {
        "SYNC": ("#00e5ff", "rgba(0, 229, 255, 0.15)"),
        "MERGE": ("#c084fc", "rgba(192, 132, 252, 0.15)"),
        "FEAT": ("#00ff66", "rgba(0, 255, 102, 0.15)"),
        "CONFIG": ("#ffbd2e", "rgba(255, 189, 46, 0.15)"),
        "DOCS": ("#38bdf8", "rgba(56, 189, 248, 0.15)"),
        "PATCH": ("#f87171", "rgba(248, 113, 113, 0.15)"),
        "COMMIT": ("#a3e635", "rgba(163, 230, 53, 0.15)"),
    }

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%">')
    
    # Defs
    svg.append("""  <defs>
    <linearGradient id="term-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0e14"/>
      <stop offset="100%" stop-color="#05080c"/>
    </linearGradient>
    <linearGradient id="term-border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.4"/>
      <stop offset="50%" stop-color="#1f2937" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#00ff66" stop-opacity="0.35"/>
    </linearGradient>
    <filter id="neon-cyan" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1.2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>""")

    # Styles
    svg.append("""  <style>
    .terminal-bg { fill: url(#term-bg); stroke: url(#term-border); stroke-width: 1.5; rx: 10; }
    .header-bar  { fill: #111822; }
    .header-title { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-size: 11.5px; fill: #6b7280; font-weight: 600; }
    .dot-red    { fill: #ff5f56; }
    .dot-yellow { fill: #ffbd2e; }
    .dot-green  { fill: #27c93f; }

    .pulse-dot {
      animation: blinkDot 1.8s infinite;
    }
    @keyframes blinkDot {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.25; }
    }

    .cursor-blink {
      animation: blinkCursor 1s infinite;
    }
    @keyframes blinkCursor {
      0%, 100% { opacity: 1; }
      50% { opacity: 0; }
    }

    .hud-label  { font-family: 'JetBrains Mono', monospace; font-size: 10.5px; fill: #64748b; font-weight: 600; }
    .hud-val-c  { font-family: 'JetBrains Mono', monospace; font-size: 10.5px; fill: #00e5ff; font-weight: 700; }
    .hud-val-g  { font-family: 'JetBrains Mono', monospace; font-size: 10.5px; fill: #00ff66; font-weight: 700; }

    .col-header { font-family: 'JetBrains Mono', monospace; font-size: 9.5px; fill: #475569; font-weight: 700; letter-spacing: 0.5px; }
    .log-date   { font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #94a3b8; }
    .log-repo   { font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #f1f5f9; font-weight: 600; }
    .log-sha    { font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #64748b; }
    .log-msg    { font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #cbd5e1; }

    .badge-txt  { font-family: 'JetBrains Mono', monospace; font-size: 8.5px; font-weight: 700; text-anchor: middle; }
    .bottom-cmd { font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #00ff66; }
    .bottom-dim { font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #475569; }
  </style>""")

    # Background window
    svg.append(f'  <rect x="2" y="2" width="{svg_width-4}" height="{svg_height-4}" class="terminal-bg"/>')

    # Top header bar
    svg.append(f'  <path d="M 2 12 C 2 6 6 2 12 2 L {svg_width-12} 2 C {svg_width-6} 2 {svg_width-2} 6 {svg_width-2} 12 L {svg_width-2} 32 L 2 32 Z" class="header-bar"/>')
    svg.append('  <circle cx="18" cy="17" r="5" class="dot-red"/>')
    svg.append('  <circle cx="33" cy="17" r="5" class="dot-yellow"/>')
    svg.append('  <circle cx="48" cy="17" r="5" class="dot-green"/>')
    svg.append(f'  <text x="{svg_width // 2}" y="21" text-anchor="middle" class="header-title">kekkan74@soc-node: ~ (tail -f /var/log/audit/git_events.log)</text>')

    # Live pulse badge on top right
    svg.append(f'  <circle cx="{svg_width - 92}" cy="17" r="3.5" fill="#00ff66" class="pulse-dot"/>')
    svg.append(f'  <text x="{svg_width - 82}" y="20.5" font-family="JetBrains Mono, monospace" font-size="9px" fill="#00ff66" font-weight="700">AUDIT_LIVE</text>')

    # Telemetry HUD Row
    svg.append('  <line x1="24" y1="52" x2="836" y2="52" stroke="#1f2937" stroke-width="0.8"/>')
    svg.append('  <text x="28" y="46">'
               f'<tspan class="hud-label">[MONITORED_NODES] </tspan><tspan class="hud-val-c">{total_repos} REPOSITORIES  </tspan>'
               f'<tspan class="hud-label">[STATUS] </tspan><tspan class="hud-val-g">🟢 DEFENSE STREAM ACTIVE  </tspan>'
               f'<tspan class="hud-label">[TELEMETRY] </tspan><tspan class="hud-val-c">ZERO-TOKEN PARSED</tspan>'
               f'</text>')

    # Column Headers
    header_y = 69
    svg.append(f'  <text x="28"  y="{header_y}" class="col-header">TIMESTAMP (UTC)</text>')
    svg.append(f'  <text x="168" y="{header_y}" class="col-header">EVENT</text>')
    svg.append(f'  <text x="248" y="{header_y}" class="col-header">REPOSITORY</text>')
    svg.append(f'  <text x="365" y="{header_y}" class="col-header">SHA</text>')
    svg.append(f'  <text x="435" y="{header_y}" class="col-header">PAYLOAD / AUDIT MESSAGE</text>')
    svg.append(f'  <line x1="24" y1="{header_y + 6}" x2="836" y2="{header_y + 6}" stroke="#1e293b" stroke-width="0.8"/>')

    # Commit Stream Rows
    start_y = 96
    row_height = 25
    for idx, c in enumerate(commits[:6]):
        cy = start_y + (idx * row_height)
        date_str = format_date(c.get("date", ""))
        c_type = c.get("type", "COMMIT")
        repo = html.escape(c.get("repo", ""))
        sha = html.escape(c.get("sha", ""))
        raw_msg = c.get("message", "")
        # Truncate message nicely
        if len(raw_msg) > 52:
            raw_msg = raw_msg[:49] + "..."
        msg = html.escape(raw_msg)

        txt_col, bg_col = badge_colors.get(c_type, ("#94a3b8", "rgba(148, 163, 184, 0.15)"))

        # Subtle row hover background
        svg.append(f'  <rect x="24" y="{cy - 14}" width="812" height="21" rx="4" fill="#0d141f" opacity="0.4"/>')

        # Date
        svg.append(f'  <text x="28" y="{cy}" class="log-date">{date_str}</text>')

        # Event Badge Box
        badge_w = 58
        badge_h = 15
        svg.append(f'  <rect x="160" y="{cy - 11}" width="{badge_w}" height="{badge_h}" rx="3" fill="{bg_col}" stroke="{txt_col}" stroke-width="0.6"/>')
        svg.append(f'  <text x="{160 + badge_w // 2}" y="{cy}" class="badge-txt" fill="{txt_col}">{c_type}</text>')

        # Repo
        svg.append(f'  <text x="248" y="{cy}" class="log-repo">{repo}</text>')

        # SHA
        svg.append(f'  <text x="365" y="{cy}" class="log-sha">{sha}</text>')

        # Commit message
        svg.append(f'  <text x="435" y="{cy}" class="log-msg">{msg}</text>')

    # Bottom Terminal Prompt
    bottom_y = svg_height - 20
    svg.append(f'  <line x1="24" y1="{bottom_y - 14}" x2="836" y2="{bottom_y - 14}" stroke="#1f2937" stroke-width="0.8"/>')
    svg.append(f'  <text x="28" y="{bottom_y}">'
               f'<tspan class="bottom-cmd">kekkan74@soc-node:~$ </tspan>'
               f'<tspan fill="#e2e8f0" font-family="JetBrains Mono, monospace" font-size="10px">git telemetry --integrity-check: 0 defects, defense perimeter active.</tspan>'
               f'<tspan fill="#00ff66" class="cursor-blink"> █</tspan>'
               f'</text>')

    svg.append('</svg>\n')

    out_dir = os.path.dirname(output_svg_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_svg_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"[+] Successfully rendered Commit Activity SVG: {output_svg_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    in_act = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base_dir, "data", "activity.json")
    out_svg = sys.argv[2] if len(sys.argv) > 2 else os.path.join(base_dir, "commit-activity.svg")
    render_commit_activity(in_act, out_svg)
