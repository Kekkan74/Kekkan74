#!/usr/bin/env python3
"""
make_info_card.py
Generates an animated terminal/neofetch-style SVG card for GitHub profile.
Features:
- Pure SVG + CSS animations (GitHub camo-compatible, zero external dependencies).
- Monospace font with terminal styling, macOS dots, and cyber glow.
- Custom Cyber-Cat ASCII art with progressive fade-in/typing animation.
- Blue Team / SOC & Python engineer specs.
"""

import html
import os
import sys

# ASCII Art: Cyber-Cat with GIT HUB core and [PYTHON // SEC // AI] chest badge
CAT_ASCII = [
    "              ..:::::::::..",
    "          ..:::''''''''''':::..",
    "       .::''   /\\       /\\   ''::.",
    "     .::'     /  \\_____/  \\     '::.",
    "    .::      /   /     \\   \\      ::.",
    "   .::      |   | (0) (0) |  |     ::.",
    "   ::       |   |   ===   |  |      ::",
    "   ::    ___\\    \\_______/   /___   ::",
    "   ::   /    '-._________.-'     \\  ::",
    "    :: |    _    |       |    _   | ::",
    "    '::.\\  / \\   |  GIT  |   / \\ /.::'",
    "      '::\\(   )  |  HUB  |  (   )/::'",
    "         \\ '--'  '-------'  '--' /",
    "      _.-'  ___________________  '-._",
    "    .'     /                   \\     '.",
    "   /      /  [PYTHON // SEC // AI] \\   \\",
    "  |______/_______________________\\______|",
    "     ((                           ))",
    "      \\\\                         //",
    "       ))                       ((",
    "      //                         \\\\"
]

PROFILE_INFO = [
    ("header", "kekkan74@soc-workstation:~$ neofetch"),
    ("separator", "------------------------------------------"),
    ("item", "[OS]", "Arch Linux // Kali Rolling"),
    ("item", "[Host]", "SOC Analyst & Threat Hunter Node"),
    ("item", "[Role]", "3rd Year Computer Engineering"),
    ("item", "[Focus]", "SOC, Blue Team & Vuln Research"),
    ("item", "[Dev]", "Python 3.13, Bash, C/C++, Git"),
    ("item", "[Sec Tools]", "Wireshark, Wazuh, Splunk, Nmap"),
    ("item", "[AI / ML]", "Scikit-Learn, PyTorch, LangChain"),
    ("item", "[Status]", "Ready for SOC / Blue Team Internships"),
    ("item", "[Quest]", "Building custom security tools & labs"),
    ("cursor_line", "kekkan74@soc-workstation:~$ ", "")
]

def generate_svg(output_path: str):
    width = 820
    height = 475
    font_size = 12
    line_height = 18.5
    start_y = 72
    cat_x = 28
    info_x = 425

    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg_parts.append("""  <defs>
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0f14"/>
      <stop offset="100%" stop-color="#05080b"/>
    </linearGradient>
    <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00ff66" stop-opacity="0.4"/>
      <stop offset="50%" stop-color="#00e5ff" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="#1f2937" stop-opacity="0.6"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1.5" result="blur" />
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>""")

    # CSS Styles & Animations
    svg_parts.append("""  <style>
    .terminal-bg { fill: url(#bg-grad); stroke: url(#border-grad); stroke-width: 1.5; rx: 12; }
    .header-bar { fill: #111822; }
    .header-title { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-size: 11.5px; fill: #6b7280; font-weight: 600; }
    .dot-red { fill: #ff5f56; }
    .dot-yellow { fill: #ffbd2e; }
    .dot-green { fill: #27c93f; }
    
    .cat-text {
      font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
      font-size: 11.5px;
      fill: #00ff66;
      white-space: pre;
      filter: drop-shadow(0 0 1.2px rgba(0, 255, 102, 0.45));
    }
    
    .info-text {
      font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
      font-size: 12px;
      white-space: pre;
    }
    
    .prompt { fill: #00e5ff; font-weight: 700; }
    .cmd { fill: #ffffff; font-weight: 600; }
    .sep { fill: #1f3b33; font-weight: 500; }
    .field-key { fill: #00e5ff; font-weight: 700; }
    .field-val { fill: #d1d5db; }
    .field-val-hi { fill: #00ff66; font-weight: 600; }
    .cursor {
      fill: #00ff66;
      animation: blink 0.9s infinite step-start;
      font-weight: 900;
    }

    @keyframes fadeIn {
      0% { opacity: 0; transform: translateY(3px); }
      100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0; }
    }
    .anim {
      opacity: 0;
      animation: fadeIn 0.4s ease-out forwards;
    }
  </style>""")

    # Window Canvas
    svg_parts.append(f'  <rect x="2" y="2" width="{width-4}" height="{height-4}" class="terminal-bg" />')
    
    # Header Bar
    svg_parts.append(f'  <path d="M 2 14 C 2 7 7 2 14 2 L {width-14} 2 C {width-7} 2 {width-2} 7 {width-2} 14 L {width-2} 36 L 2 36 Z" class="header-bar" />')
    svg_parts.append('  <circle cx="20" cy="19" r="6" class="dot-red" />')
    svg_parts.append('  <circle cx="38" cy="19" r="6" class="dot-yellow" />')
    svg_parts.append('  <circle cx="56" cy="19" r="6" class="dot-green" />')
    svg_parts.append(f'  <text x="{width // 2}" y="23" text-anchor="middle" class="header-title">kekkan74@soc-node: ~ (neofetch)</text>')

    # 1. Cat ASCII column (progressive animation)
    delay = 0.05
    for idx, line in enumerate(CAT_ASCII):
        y = start_y + (idx * line_height)
        esc_line = html.escape(line)
        svg_parts.append(f'  <text x="{cat_x}" y="{y}" class="cat-text anim" style="animation-delay: {delay:.2f}s;">{esc_line}</text>')
        delay += 0.04

    # 2. Info column (progressive animation)
    info_y_offset = start_y + 12
    for item in PROFILE_INFO:
        kind = item[0]
        delay += 0.07
        
        if kind == "header":
            prompt_user = html.escape("kekkan74@soc-workstation:~$ ")
            cmd_text = html.escape("neofetch")
            svg_parts.append(
                f'  <text x="{info_x}" y="{info_y_offset}" class="info-text anim" style="animation-delay: {delay:.2f}s;">'
                f'<tspan class="prompt">{prompt_user}</tspan>'
                f'<tspan class="cmd">{cmd_text}</tspan>'
                f'</text>'
            )
        elif kind == "separator":
            sep_line = html.escape(item[1])
            svg_parts.append(
                f'  <text x="{info_x}" y="{info_y_offset}" class="info-text anim" style="animation-delay: {delay:.2f}s;">'
                f'<tspan class="sep">{sep_line}</tspan>'
                f'</text>'
            )
        elif kind == "item":
            key_text = f"{item[1]:<13}"
            val_text = item[2]
            esc_key = html.escape(key_text)
            esc_val = html.escape(val_text)
            
            # Highlight status or focus with green
            val_class = "field-val-hi" if item[1] in ("[Status]", "[Focus]") else "field-val"
            svg_parts.append(
                f'  <text x="{info_x}" y="{info_y_offset}" class="info-text anim" style="animation-delay: {delay:.2f}s;">'
                f'<tspan class="field-key">{esc_key}</tspan>'
                f'<tspan class="{val_class}">{esc_val}</tspan>'
                f'</text>'
            )
        elif kind == "cursor_line":
            prompt_user = html.escape(item[1])
            svg_parts.append(
                f'  <text x="{info_x}" y="{info_y_offset + 6}" class="info-text anim" style="animation-delay: {delay:.2f}s;">'
                f'<tspan class="prompt">{prompt_user}</tspan>'
                f'<tspan class="cursor">█</tspan>'
                f'</text>'
            )
        
        info_y_offset += line_height + 4.5

    svg_parts.append('</svg>\n')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
    print(f"[+] Successfully generated SVG: {output_path}")

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(out_dir, "info-card.svg")
    generate_svg(target)

