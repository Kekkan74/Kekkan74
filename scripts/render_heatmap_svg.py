#!/usr/bin/env python3
"""
render_heatmap_svg.py
Reads data/contributions.json and generates an animated terminal-styled
contribution heatmap SVG with diagonal wave animation in terminal/cyber green.
Zero tokens, 100% SVG + CSS, GitHub camo-compatible.
"""

import json
import os
import sys
from datetime import datetime

def render_heatmap(json_path: str, output_svg: str):
    if not os.path.exists(json_path):
        print(f"[!] Input JSON not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    username = data.get("username", "Kekkan74")
    total_contribs = data.get("total_contributions", 0)
    longest_streak = data.get("longest_streak", 0)
    current_streak = data.get("current_streak", 0)
    days = data.get("days", [])

    # Group into weeks (each starting Sunday=0, ending Saturday=6)
    weeks = []
    current_week = []
    for d in days:
        current_week.append(d)
        if d.get("weekday") == 6:
            weeks.append(current_week)
            current_week = []
    if current_week:
        weeks.append(current_week)

    # Detect month positions
    month_labels = []
    last_month = None
    for col_idx, week in enumerate(weeks):
        for d in week:
            dt = datetime.strptime(d["date"], "%Y-%m-%d")
            m_name = dt.strftime("%b")
            if m_name != last_month and dt.day <= 7:
                month_labels.append((col_idx, m_name))
                last_month = m_name
                break

    # Dimensions
    svg_width = 820
    svg_height = 240
    cell_size = 10.5
    cell_gap = 3.2
    step = cell_size + cell_gap

    grid_start_x = 54
    grid_start_y = 102

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%">')
    
    # Defs & Gradients
    svg.append("""  <defs>
    <linearGradient id="heat-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0e14"/>
      <stop offset="100%" stop-color="#05080c"/>
    </linearGradient>
    <linearGradient id="heat-border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00ff66" stop-opacity="0.35"/>
      <stop offset="50%" stop-color="#1f2937" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#00e5ff" stop-opacity="0.2"/>
    </linearGradient>
    <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>""")

    # CSS styles
    svg.append("""  <style>
    .terminal-bg { fill: url(#heat-bg); stroke: url(#heat-border); stroke-width: 1.4; rx: 10; }
    .header-bar { fill: #111822; }
    .header-title { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 11.5px; fill: #6b7280; font-weight: 600; }
    .dot-red { fill: #ff5f56; }
    .dot-yellow { fill: #ffbd2e; }
    .dot-green { fill: #27c93f; }

    .stat-label { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 11px; fill: #00e5ff; font-weight: 700; }
    .stat-val   { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 11px; fill: #d1d5db; }
    .stat-hi    { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 11px; fill: #00ff66; font-weight: 700; }

    .axis-label { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 9.5px; fill: #64748b; font-weight: 500; }

    /* Terminal Cyber Green Cell Palette */
    .lvl-0 { fill: #151c24; }
    .lvl-1 { fill: #0e4429; }
    .lvl-2 { fill: #006d32; }
    .lvl-3 { fill: #26a641; }
    .lvl-4 { fill: #00ff66; filter: drop-shadow(0 0 2px rgba(0, 255, 102, 0.75)); }

    /* Diagonal wave animation */
    @keyframes heatRipple {
      0% {
        opacity: 0;
        transform: scale(0.3);
      }
      65% {
        opacity: 1;
        transform: scale(1.15);
      }
      100% {
        opacity: 1;
        transform: scale(1);
      }
    }

    .heat-cell {
      transform-box: fill-box;
      transform-origin: center;
      opacity: 0;
      animation: heatRipple 0.35s ease-out forwards;
    }
  </style>""")

    # Background window
    svg.append(f'  <rect x="2" y="2" width="{svg_width-4}" height="{svg_height-4}" class="terminal-bg"/>')

    # Top header bar
    svg.append(f'  <path d="M 2 12 C 2 6 6 2 12 2 L {svg_width-12} 2 C {svg_width-6} 2 {svg_width-2} 6 {svg_width-2} 12 L {svg_width-2} 32 L 2 32 Z" class="header-bar"/>')
    svg.append('  <circle cx="18" cy="17" r="5" class="dot-red"/>')
    svg.append('  <circle cx="33" cy="17" r="5" class="dot-yellow"/>')
    svg.append('  <circle cx="48" cy="17" r="5" class="dot-green"/>')
    svg.append(f'  <text x="{svg_width // 2}" y="21" text-anchor="middle" class="header-title">kekkan74@soc-node: ~ (git activity-heatmap)</text>')

    # Stats subheader
    stats_y = 54
    svg.append(f'  <text x="54" y="{stats_y}">'
               f'<tspan class="stat-label">[TOTAL] </tspan><tspan class="stat-hi">{total_contribs}</tspan><tspan class="stat-val"> contributions in past year  </tspan>'
               f'<tspan class="stat-label">[STREAK] </tspan><tspan class="stat-val">Best: </tspan><tspan class="stat-hi">{longest_streak}d  </tspan>'
               f'<tspan class="stat-label">[STATUS] </tspan><tspan class="stat-hi">Active Hunter</tspan>'
               f'</text>')

    # Month Labels
    month_y = grid_start_y - 8
    for col_idx, m_name in month_labels:
        mx = grid_start_x + (col_idx * step)
        svg.append(f'  <text x="{mx}" y="{month_y}" class="axis-label">{m_name}</text>')

    # Weekday Labels (Mon=1, Wed=3, Fri=5)
    day_labels = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    for row_idx, label in day_labels:
        dy = grid_start_y + (row_idx * step) + 8.5
        svg.append(f'  <text x="{grid_start_x - 28}" y="{dy}" class="axis-label">{label}</text>')

    # Calendar Cells Grid with diagonal wave delay
    for col_idx, week in enumerate(weeks):
        for d in week:
            row_idx = d["weekday"]
            lvl = d.get("level", 0)
            cnt = d.get("count", 0)
            date_str = d.get("date", "")

            cx = grid_start_x + (col_idx * step)
            cy = grid_start_y + (row_idx * step)

            # Diagonal delay: (col + row) gives the diagonal wave direction
            diag_val = col_idx + row_idx
            delay = 0.05 + (diag_val * 0.015)

            tip = f"{cnt} contributions on {date_str}" if cnt > 0 else f"No contributions on {date_str}"
            svg.append(
                f'  <rect x="{cx:.1f}" y="{cy:.1f}" width="{cell_size}" height="{cell_size}" rx="2" '
                f'class="lvl-{lvl} heat-cell" style="animation-delay: {delay:.3f}s;">'
                f'<title>{tip}</title>'
                f'</rect>'
            )

    # Legend at bottom
    legend_y = svg_height - 22
    legend_right_x = grid_start_x + (len(weeks) * step) - 5
    svg.append(f'  <text x="{legend_right_x - 110}" y="{legend_y + 8}" class="axis-label">Less</text>')
    for i in range(5):
        lx = legend_right_x - 80 + (i * (cell_size + 2.5))
        svg.append(f'  <rect x="{lx}" y="{legend_y}" width="{cell_size}" height="{cell_size}" rx="2" class="lvl-{i}"/>')
    svg.append(f'  <text x="{legend_right_x + 10}" y="{legend_y + 8}" class="axis-label">More</text>')

    svg.append('</svg>\n')

    with open(output_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"[+] Successfully rendered Heatmap SVG: {output_svg}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    in_json = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base_dir, "data", "contributions.json")
    out_svg = sys.argv[2] if len(sys.argv) > 2 else os.path.join(base_dir, "contrib-heatmap.svg")
    render_heatmap(in_json, out_svg)

