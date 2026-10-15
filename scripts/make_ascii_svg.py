#!/usr/bin/env python3
"""
make_ascii_svg.py
Renders the dual-color GitHub Invertocat ASCII art logo to profile-ascii.svg.
Features:
- Split at column 26:
  - Left half: Vibrant bright orange (#FF8C00)
  - Right half: Charcoal gray / stealth black (#484F58) with high-contrast subtle glow against #0D1117
- Glowing Ocular Reticles / Eyes:
  - Left Eye ( | ): Glowing yellow/amber (#FFD700)
  - Right Eye ( | ): Glowing terminal cyber green & white (#00FF66 / #FFFFFF)
- Progressive line-by-line typing animation from top to bottom
- macOS terminal controls and active prompt cursor
"""

import html
import os
import sys

# Official 17-line GitHub Invertocat ASCII art (centered at column 26)
OCTOCAT_LOGO = [
    "            .-----------------------------.          ",
    "         .-----------------------------------.       ",
    "       .---------..-----------------..---------.     ",
    "     .---------/    \\-------------/    \\---------.   ",
    "    .---------|      '-----------'      |---------.  ",
    "   .----------|                         |----------. ",
    "   .---------/     \\___         ___/     \\---------. ",
    "  .---------|      ( | )       ( | )      |---------.",
    "  .---------|       ---         ---       |---------.",
    "  .----------\\            _v_            /----------.",
    "   .----------'-.                     .-'----------. ",
    "   .-------------\\                   /-------------. ",
    "    .-----.._     |                 |         .---.  ",
    "     .-------'-.  |                 |       .-----.  ",
    "       .--------\\ |     .-----.     |     .-----.    ",
    "         .-------\\|    |-------|    |   .-----.      ",
    "            '-----|____|-------|____| .-----'        "
]

def format_left_half(text: str, row_idx: int) -> str:
    """Styles the left half with #FF8C00 and #FFD700 for the left eye."""
    # Line 7 contains the eyes: '  .---------|      ( | )   '
    if row_idx == 7 and "( | )" in text:
        eye_pos = text.find("( | )")
        before_eye = html.escape(text[:eye_pos])
        eye = html.escape("( | )")
        after_eye = html.escape(text[eye_pos + 5:])
        return (
            f'<tspan class="part-left">{before_eye}</tspan>'
            f'<tspan class="eye-left">{eye}</tspan>'
            f'<tspan class="part-left">{after_eye}</tspan>'
        )
    
    # Line 8 contains the left brow '---'
    if row_idx == 8 and "---" in text:
        brow_pos = text.find("---")
        before_brow = html.escape(text[:brow_pos])
        brow = html.escape("---")
        after_brow = html.escape(text[brow_pos + 3:])
        return (
            f'<tspan class="part-left">{before_brow}</tspan>'
            f'<tspan class="eye-left-brow">{brow}</tspan>'
            f'<tspan class="part-left">{after_brow}</tspan>'
        )

    return f'<tspan class="part-left">{html.escape(text)}</tspan>'

def format_right_half(text: str, row_idx: int) -> str:
    """Styles the right half with #484F58 and #00FF66 / #FFFFFF for the right eye."""
    # Line 7 contains the right eye: '   ( | )      |---------.'
    if row_idx == 7 and "( | )" in text:
        eye_pos = text.find("( | )")
        before_eye = html.escape(text[:eye_pos])
        eye = html.escape("( | )")
        after_eye = html.escape(text[eye_pos + 5:])
        return (
            f'<tspan class="part-right">{before_eye}</tspan>'
            f'<tspan class="eye-right">{eye}</tspan>'
            f'<tspan class="part-right">{after_eye}</tspan>'
        )

    # Line 8 contains the right brow '---'
    if row_idx == 8 and "---" in text:
        brow_pos = text.find("---")
        before_brow = html.escape(text[:brow_pos])
        brow = html.escape("---")
        after_brow = html.escape(text[brow_pos + 3:])
        return (
            f'<tspan class="part-right">{before_brow}</tspan>'
            f'<tspan class="eye-right-brow">{brow}</tspan>'
            f'<tspan class="part-right">{after_brow}</tspan>'
        )

    return f'<tspan class="part-right">{html.escape(text)}</tspan>'

def generate_ascii_svg(output_path: str):
    width = 680
    height = 450
    font_size = 13.5
    line_height = 18.5
    start_y = 75
    text_x = 48

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    
    # Gradients & Filters
    svg.append("""  <defs>
    <linearGradient id="term-border" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FF8C00" stop-opacity="0.45"/>
      <stop offset="50%" stop-color="#30363d" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#00FF66" stop-opacity="0.35"/>
    </linearGradient>
  </defs>""")

    # Styles
    svg.append("""  <style>
    .terminal-bg { fill: #0D1117; stroke: url(#term-border); stroke-width: 1.4; rx: 10; }
    .header-bar { fill: #161b22; }
    .header-title { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 11.5px; fill: #8b949e; font-weight: 600; }
    .dot-red { fill: #ff5f56; }
    .dot-yellow { fill: #ffbd2e; }
    .dot-green { fill: #27c93f; }

    .ascii-row {
      font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
      font-size: 13.5px;
      white-space: pre;
    }

    /* Left Half: Bright Orange */
    .part-left {
      fill: #FF8C00;
      font-weight: 700;
      filter: drop-shadow(0 0 1.2px rgba(255, 140, 0, 0.4));
    }

    /* Left Eye: Radiant Amber/Yellow */
    .eye-left {
      fill: #FFD700;
      font-weight: 900;
      filter: drop-shadow(0 0 3px rgba(255, 215, 0, 0.95));
    }
    .eye-left-brow {
      fill: #FFA500;
      font-weight: 800;
    }

    /* Right Half: Charcoal Gray / Dark Steel with crisp contrast on #0D1117 */
    .part-right {
      fill: #484F58;
      font-weight: 700;
      filter: drop-shadow(0 0 1px rgba(110, 118, 129, 0.25));
    }

    /* Right Eye: Terminal Cyber Green / White Glow */
    .eye-right {
      fill: #00FF66;
      font-weight: 900;
      filter: drop-shadow(0 0 3px rgba(0, 255, 102, 0.95));
    }
    .eye-right-brow {
      fill: #2ea043;
      font-weight: 800;
    }

    /* Prompt and Cursor */
    .prompt-text {
      font-family: 'JetBrains Mono', 'Fira Code', monospace;
      font-size: 12px;
      font-weight: 600;
    }
    .prompt-user { fill: #58a6ff; }
    .cursor {
      fill: #00FF66;
      animation: blink 0.9s infinite step-start;
      font-weight: 900;
    }

    @keyframes fadeIn {
      0%   { opacity: 0; transform: translateY(2px); }
      100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes blink {
      0%, 100% { opacity: 1; }
      50%      { opacity: 0; }
    }

    .anim-row {
      opacity: 0;
      animation: fadeIn 0.35s ease-out forwards;
    }
  </style>""")

    # Background window (#0D1117)
    svg.append(f'  <rect x="2" y="2" width="{width-4}" height="{height-4}" class="terminal-bg"/>')

    # Top Header Bar
    svg.append(f'  <path d="M 2 12 C 2 6 6 2 12 2 L {width-12} 2 C {width-6} 2 {width-2} 6 {width-2} 12 L {width-2} 32 L 2 32 Z" class="header-bar"/>')
    svg.append('  <circle cx="18" cy="17" r="5" class="dot-red"/>')
    svg.append('  <circle cx="33" cy="17" r="5" class="dot-yellow"/>')
    svg.append('  <circle cx="48" cy="17" r="5" class="dot-green"/>')
    svg.append(f'  <text x="{width // 2}" y="21" text-anchor="middle" class="header-title">kekkan74@soc-node: ~ (github-invertocat.ascii)</text>')

    # ASCII Lines with line-by-line typing animation
    delay = 0.05
    for idx, line in enumerate(OCTOCAT_LOGO):
        left_txt = line[:26]
        right_txt = line[26:]
        
        y = start_y + (idx * line_height)
        esc_left = format_left_half(left_txt, idx)
        esc_right = format_right_half(right_txt, idx)

        svg.append(
            f'  <text x="{text_x}" y="{y:.1f}" class="ascii-row anim-row" style="animation-delay: {delay:.2f}s;">'
            f'{esc_left}{esc_right}'
            f'</text>'
        )
        delay += 0.04

    # Bottom Prompt
    prompt_y = height - 22
    cursor_delay = delay + 0.08
    svg.append(
        f'  <text x="{text_x}" y="{prompt_y}" class="prompt-text anim-row" style="animation-delay: {cursor_delay:.2f}s;">'
        f'<tspan class="prompt-user">kekkan74@soc-node:~$ </tspan>'
        f'<tspan class="cursor">█</tspan>'
        f'</text>'
    )

    svg.append('</svg>\n')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"[+] Successfully generated Invertocat ASCII SVG: {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base_dir, "profile-ascii.svg")
    generate_ascii_svg(target)
