#!/usr/bin/env python3
"""
render_heatmap_svg.py
Reads data/contributions.json and generates an upgraded, animated terminal-styled
contribution heatmap SVG with telemetry HUD cards, activity distribution bar,
and diagonal wave animation in terminal/cyber green.
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
    total_contribs = data.get("total_contributions", 12)
    longest_streak = data.get("longest_streak", 2)
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
    svg_width = 860
    svg_height = 345
    cell_size = 10.5
    cell_gap = 3.2
    step = cell_size + cell_gap

    grid_start_x = 64
    grid_start_y = 150

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%">')
    
    # Defs & Gradients
    svg.append("""  <defs>
    <linearGradient id="heat-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0e14"/>
      <stop offset="100%" stop-color="#05080c"/>
    </linearGradient>
    <linearGradient id="heat-border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00ff66" stop-opacity="0.45"/>
      <stop offset="50%" stop-color="#1f2937" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#00e5ff" stop-opacity="0.4"/>
    </linearGradient>
    <linearGradient id="hud-card-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#111823"/>
      <stop offset="100%" stop-color="#0b1017"/>
    </linearGradient>
    <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1.8" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>""")

    # CSS styles
    svg.append("""  <style>
    .terminal-bg { fill: url(#heat-bg); stroke: url(#heat-border); stroke-width: 1.5; rx: 10; }
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

    /* HUD Metrics Cards */
    .hud-box    { fill: url(#hud-card-grad); stroke: #1e293b; stroke-width: 0.8; rx: 6; }
    .hud-title  { font-family: 'JetBrains Mono', monospace; font-size: 8.5px; fill: #64748b; font-weight: 700; letter-spacing: 0.8px; }
    .hud-val-g  { font-family: 'JetBrains Mono', monospace; font-size: 17px; fill: #00ff66; font-weight: 800; }
    .hud-val-c  { font-family: 'JetBrains Mono', monospace; font-size: 17px; fill: #00e5ff; font-weight: 800; }
    .hud-val-a  { font-family: 'JetBrains Mono', monospace; font-size: 17px; fill: #ffbd2e; font-weight: 800; }
    .hud-val-s  { font-family: 'JetBrains Mono', monospace; font-size: 13.5px; fill: #00ff66; font-weight: 800; }
    .hud-sub    { font-family: 'JetBrains Mono', monospace; font-size: 8px; fill: #475569; }

    .axis-label { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 9.5px; fill: #64748b; font-weight: 500; }

    /* Terminal Cyber Green Cell Palette */
    .lvl-0 { fill: #0e141d; stroke: #151e2b; stroke-width: 0.6; }
    .lvl-1 { fill: #0e4429; stroke: #185a37; stroke-width: 0.6; }
    .lvl-2 { fill: #006d32; stroke: #009944; stroke-width: 0.6; }
    .lvl-3 { fill: #26a641; filter: drop-shadow(0 0 1.5px rgba(38, 166, 65, 0.7)); }
    .lvl-4 { fill: #00ff66; filter: drop-shadow(0 0 3px rgba(0, 255, 102, 0.95)); }

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

    .dist-label { font-family: 'JetBrains Mono', monospace; font-size: 9px; font-weight: 600; }
    .cmd-text   { font-family: 'JetBrains Mono', monospace; font-size: 9.5px; fill: #00ff66; }
    .cmd-dim    { font-family: 'JetBrains Mono', monospace; font-size: 9.5px; fill: #64748b; }
  </style>""")

    # Background window
    svg.append(f'  <rect x="2" y="2" width="{svg_width-4}" height="{svg_height-4}" class="terminal-bg"/>')

    # Top header bar
    svg.append(f'  <path d="M 2 12 C 2 6 6 2 12 2 L {svg_width-12} 2 C {svg_width-6} 2 {svg_width-2} 6 {svg_width-2} 12 L {svg_width-2} 32 L 2 32 Z" class="header-bar"/>')
    svg.append('  <circle cx="18" cy="17" r="5" class="dot-red"/>')
    svg.append('  <circle cx="33" cy="17" r="5" class="dot-yellow"/>')
    svg.append('  <circle cx="48" cy="17" r="5" class="dot-green"/>')
    svg.append(f'  <text x="{svg_width // 2}" y="21" text-anchor="middle" class="header-title">kekkan74@soc-node: ~ (git activity-heatmap --live-radar)</text>')

    # Live pulse badge on top right
    svg.append(f'  <circle cx="{svg_width - 110}" cy="17" r="3.5" fill="#00ff66" class="pulse-dot"/>')
    svg.append(f'  <text x="{svg_width - 100}" y="20.5" font-family="JetBrains Mono, monospace" font-size="9px" fill="#00ff66" font-weight="700">LIVE_RADAR</text>')

    # 4 HUD Metrics Cards
    hud_y = 44
    card_w = 192
    card_h = 50
    spacing = 14

    # Card 1: Total Commits
    c1_x = 24
    svg.append(f'  <rect x="{c1_x}" y="{hud_y}" width="{card_w}" height="{card_h}" class="hud-box"/>')
    svg.append(f'  <text x="{c1_x + 12}" y="{hud_y + 15}" class="hud-title">TOTAL CONTRIBUTIONS</text>')
    svg.append(f'  <text x="{c1_x + 12}" y="{hud_y + 35}" class="hud-val-g">{total_contribs} <tspan font-size="11px" fill="#64748b" font-weight="500">COMMITS</tspan></text>')
    svg.append(f'  <text x="{c1_x + 12}" y="{hud_y + 45}" class="hud-sub">PAST 365 DAYS ACTIVE</text>')

    # Card 2: Streak Stats
    c2_x = c1_x + card_w + spacing
    svg.append(f'  <rect x="{c2_x}" y="{hud_y}" width="{card_w}" height="{card_h}" class="hud-box"/>')
    svg.append(f'  <text x="{c2_x + 12}" y="{hud_y + 15}" class="hud-title">LONGEST STREAK</text>')
    svg.append(f'  <text x="{c2_x + 12}" y="{hud_y + 35}" class="hud-val-c">{longest_streak} <tspan font-size="11px" fill="#64748b" font-weight="500">DAYS</tspan></text>')
    svg.append(f'  <text x="{c2_x + 12}" y="{hud_y + 45}" class="hud-sub">PERSISTENT CADENCE</text>')

    # Card 3: Monitored Repos
    c3_x = c2_x + card_w + spacing
    svg.append(f'  <rect x="{c3_x}" y="{hud_y}" width="{card_w}" height="{card_h}" class="hud-box"/>')
    svg.append(f'  <text x="{c3_x + 12}" y="{hud_y + 15}" class="hud-title">MONITORED REPOS</text>')
    svg.append(f'  <text x="{c3_x + 12}" y="{hud_y + 35}" class="hud-val-a">4 <tspan font-size="11px" fill="#64748b" font-weight="500">TARGETS</tspan></text>')
    svg.append(f'  <text x="{c3_x + 12}" y="{hud_y + 45}" class="hud-sub">TOP-GLOBALES // DOTFILES // CS</text>')

    # Card 4: Operational Status
    c4_x = c3_x + card_w + spacing
    svg.append(f'  <rect x="{c4_x}" y="{hud_y}" width="{card_w + 2}" height="{card_h}" class="hud-box"/>')
    svg.append(f'  <text x="{c4_x + 12}" y="{hud_y + 15}" class="hud-title">SYSTEM STATUS</text>')
    svg.append(f'  <text x="{c4_x + 12}" y="{hud_y + 35}" class="hud-val-s">🟢 OPERATIONAL</text>')
    svg.append(f'  <text x="{c4_x + 12}" y="{hud_y + 45}" class="hud-sub">AUTONOMOUS CI/CD PIPELINE</text>')

    # Divider below HUD
    svg.append('  <line x1="24" y1="106" x2="836" y2="106" stroke="#1f2937" stroke-width="0.8"/>')

    # Month Labels
    month_y = grid_start_y - 9
    for col_idx, m_name in month_labels:
        mx = grid_start_x + (col_idx * step)
        svg.append(f'  <text x="{mx}" y="{month_y}" class="axis-label">{m_name}</text>')

    # Weekday Labels (Mon=1, Wed=3, Fri=5)
    day_labels = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    for row_idx, label in day_labels:
        dy = grid_start_y + (row_idx * step) + 8.5
        svg.append(f'  <text x="{grid_start_x - 30}" y="{dy}" class="axis-label">{label}</text>')

    # Calendar Cells Grid with diagonal wave delay
    for col_idx, week in enumerate(weeks):
        for d in week:
            row_idx = d["weekday"]
            lvl = d.get("level", 0)
            cnt = d.get("count", 0)
            date_str = d.get("date", "")

            cx = grid_start_x + (col_idx * step)
            cy = grid_start_y + (row_idx * step)

            diag_val = col_idx + row_idx
            delay = 0.05 + (diag_val * 0.015)

            tip = f"{cnt} contributions on {date_str}" if cnt > 0 else f"No contributions on {date_str}"
            svg.append(
                f'  <rect x="{cx:.1f}" y="{cy:.1f}" width="{cell_size}" height="{cell_size}" rx="2.5" '
                f'class="lvl-{lvl} heat-cell" style="animation-delay: {delay:.3f}s;">'
                f'<title>{tip}</title>'
                f'</rect>'
            )

    # Divider below Heatmap
    bar_top_y = grid_start_y + (7 * step) + 12
    svg.append(f'  <line x1="24" y1="{bar_top_y}" x2="836" y2="{bar_top_y}" stroke="#1f2937" stroke-width="0.8"/>')

    # Monitored Repos Activity Distribution Bar
    dist_y = bar_top_y + 16
    svg.append(f'  <text x="28" y="{dist_y}" font-family="JetBrains Mono, monospace" font-size="8.5px" fill="#64748b" font-weight="700">COMMIT VELOCITY DISTRIBUTION BY TARGET REPOSITORY:</text>')

    prog_y = dist_y + 7
    total_bar_w = 808
    # Segments: Top-Globales (38%), Kekkan74 (28%), dotfiles (20%), apuntesPython (14%)
    w_top = int(total_bar_w * 0.38)
    w_kek = int(total_bar_w * 0.28)
    w_dot = int(total_bar_w * 0.20)
    w_apu = total_bar_w - (w_top + w_kek + w_dot)

    bx = 26
    svg.append(f'  <rect x="{bx}" y="{prog_y}" width="{w_top}" height="6" rx="3" fill="#00e5ff"/>')
    bx += w_top + 2
    svg.append(f'  <rect x="{bx}" y="{prog_y}" width="{w_kek}" height="6" rx="3" fill="#00ff66"/>')
    bx += w_kek + 2
    svg.append(f'  <rect x="{bx}" y="{prog_y}" width="{w_dot}" height="6" rx="3" fill="#c084fc"/>')
    bx += w_dot + 2
    svg.append(f'  <rect x="{bx}" y="{prog_y}" width="{w_apu}" height="6" rx="3" fill="#ffbd2e"/>')

    # Distribution Legend Badges
    leg_dist_y = prog_y + 16
    svg.append(f'  <text x="28" y="{leg_dist_y}">'
               f'<tspan fill="#00e5ff" class="dist-label">● Top-Globales (38%)  </tspan>'
               f'<tspan fill="#00ff66" class="dist-label">● Kekkan74 (28%)  </tspan>'
               f'<tspan fill="#c084fc" class="dist-label">● dotfiles (20%)  </tspan>'
               f'<tspan fill="#ffbd2e" class="dist-label">● apuntesPython (14%)</tspan>'
               f'</text>')

    # Footer line & Legend at bottom
    legend_y = svg_height - 18
    svg.append(f'  <line x1="24" y1="{legend_y - 12}" x2="836" y2="{legend_y - 12}" stroke="#1f2937" stroke-width="0.8"/>')
    svg.append(f'  <text x="28" y="{legend_y + 2}">'
               f'<tspan class="cmd-text">kekkan74@soc-node:~$ </tspan>'
               f'<tspan class="cmd-dim">audit-check: 0 telemetry defects, all engineering nodes nominal.</tspan>'
               f'<tspan fill="#00ff66" class="cursor-blink"> █</tspan>'
               f'</text>')

    legend_right_x = grid_start_x + (len(weeks) * step)
    svg.append(f'  <text x="{legend_right_x - 115}" y="{legend_y + 2}" class="axis-label">Less</text>')
    for i in range(5):
        lx = legend_right_x - 85 + (i * (cell_size + 2.5))
        svg.append(f'  <rect x="{lx}" y="{legend_y - 6}" width="{cell_size}" height="{cell_size}" rx="2" class="lvl-{i}"/>')
    svg.append(f'  <text x="{legend_right_x + 5}" y="{legend_y + 2}" class="axis-label">More</text>')

    svg.append('</svg>\n')

    out_dir = os.path.dirname(output_svg)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"[+] Successfully rendered Upgraded Heatmap SVG: {output_svg}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    in_json = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base_dir, "data", "contributions.json")
    out_svg = sys.argv[2] if len(sys.argv) > 2 else os.path.join(base_dir, "contrib-heatmap.svg")
    render_heatmap(in_json, out_svg)
