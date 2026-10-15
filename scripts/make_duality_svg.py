#!/usr/bin/env python3
"""
make_duality_svg.py
Renders the updated Octocat Duality terminal ASCII art in high-fidelity SVG.
Features:
- Dual-color palette: Vibrant fiery orange on the left, stealth black / deep dark blue on the right.
- Custom Cyber/Sharingan ocular reticle in both eyes (Left: Golden Amber, Right: Deep Stealth Blue).
- Vertical dividing pipe line '|' at exact center.
- Whiskers and curling tentacles matching the terminal aesthetic.
- Terminal frame with '[OCTOCAT // DUALITY // ACTIVE]' tags and 'bash-@-kekkan74 ~ > █' prompt.
- Progressive scanline animation via CSS keyframes.
"""

import html
import os
import sys

# Exact lines with pipe '|' at index 29 (and padded whiskers on left and right)
RAW_DUALITY_LINES = [
    # 0
    "               .ooo.         |         ..**:.                        ",
    # 1
    "            .::::::oox::oo   |  ...  .*###WW@%                       ",
    # 2
    "           o::::::::::oox:.. | ....*#########@$                      ",
    # 3
    "           o::::::::::::ddMMM|##*###############$                    ",
    # 4
    "           x::::::::xdddMMMMM|##################$                    ",
    # 5
    "           ::::::xddddmMMMMMM|##################@                    ",
    # 6
    "           ::::xxddddmMMMMMMM|###################@                   ",
    # 7
    "           :::odddmmmmMMMMMMM|###WWWWWWWWWWWWWWWW@                   ",
    # 8
    "           :::odddmmmmMMMMMMM|###WWWWWWWWWWWWWWWW@                   ",
    # 9
    "          :::::ddddm..OMMMMMM|************#######.                   ",
    # 10 - Eye reticle starts
    "          o:::  /\\_     oox::|**     _/\\  ******$                    ",
    # 11
    "          o::  / | \\  xxxx*::|**    / | \\  .****$                    ",
    # 12
    "          ::: |  |  | xx::xx:|..   |  |  | ....#$                    ",
    # 13
    "          :::: \\ | / x:x..x: |..   \\ | / ......#$                    ",
    # 14
    "          x:::  \\/    oxxx.  | .    \\/  .......#$                    ",
    # 15
    "          ::&:::oo::oxxxM  x:|.......*%@.......#$                    ",
    # 16
    "          xx::::oo::oxxx   x:|........%#.......#$                    ",
    # 17 - Whiskers start
    "..******************xxndoo::ooxxxxxx.x  | .......#........#*****************..",
    "  ***************:xxddo:ooxxxxxdmmMMM|.................#***************      ",
    "     ************xddddoxoxxxxxmmmmmm|.................************          ",
    "        *********'xxdddooxoxxmmmmmMM|................*********              ",
    "           ******  :kddxddoxmmmmmmMM|................'******                ",
    # 22
    "                  ..:oxx*#%@ |######M******                          ",
    # 23
    "                   ..MMMM%@@ |######.......                          ",
    # 24
    "                  .MMMM%@@   |************                           ",
    # 25
    "                .:MMMM%@@    |***********                            ",
    # 26 - Left tentacle
    "  oxd:       xddddddmMINMM@@ |WW%%$ ##%@$                            ",
    "   :xxod:     *oxoxxx*MM@%   |WW%%$ #%@@                             ",
    "     :xda\"           #%@%    |WW%%$ #%@@                             ",
    "                     #%@%    |WW%%$ #%@@                             ",
    "                     #%@%    |WW%%$ #%@@                             ",
    "                     ###%    |'W%%$ w%@@                             ",
    "                     :x::'   |W%%$.  ..$.                            "
]

def format_left(text: str, row_idx: int) -> str:
    """Styles the left orange side with glowing ocular reticle for rows 10-14."""
    if 10 <= row_idx <= 14:
        res = ""
        for col_idx, ch in enumerate(text):
            esc = html.escape(ch)
            if 14 <= col_idx <= 22 and ch in ('/', '\\', '|', '_'):
                res += f'<tspan class="eye-reticle-or">{esc}</tspan>'
            elif ch in ('M', 'm', 'd', 'o', 'x'):
                res += f'<tspan class="or-bright">{esc}</tspan>'
            elif ch in ('*', '.', ':', "'", '"'):
                res += f'<tspan class="or-dim">{esc}</tspan>'
            else:
                res += f'<tspan class="or-mid">{esc}</tspan>'
        return res

    res = ""
    for ch in text:
        esc = html.escape(ch)
        if ch in ('M', 'm', 'd', '@', '%'):
            res += f'<tspan class="or-bright">{esc}</tspan>'
        elif ch in ('*', '.', ':', "'", '"'):
            res += f'<tspan class="or-dim">{esc}</tspan>'
        else:
            res += f'<tspan class="or-mid">{esc}</tspan>'
    return res

def format_right(text: str, row_idx: int) -> str:
    """Styles the right side with Stealth Black / Deep Midnight Dark Blue."""
    if 10 <= row_idx <= 14:
        res = ""
        for col_idx, ch in enumerate(text):
            esc = html.escape(ch)
            # Ocular reticle between columns 6 and 16 on right
            if 6 <= col_idx <= 16 and ch in ('/', '\\', '|', '_'):
                res += f'<tspan class="eye-reticle-bl">{esc}</tspan>'
            elif ch in ('#', 'W', '@', '%', '$', 'M'):
                res += f'<tspan class="bl-bright">{esc}</tspan>'
            elif ch in ('.', '*', "'"):
                res += f'<tspan class="bl-dim">{esc}</tspan>'
            else:
                res += f'<tspan class="bl-mid">{esc}</tspan>'
        return res

    res = ""
    for ch in text:
        esc = html.escape(ch)
        if ch in ('#', 'W', '@', '%', '$', 'M'):
            res += f'<tspan class="bl-bright">{esc}</tspan>'
        elif ch in ('.', '*', "'"):
            res += f'<tspan class="bl-dim">{esc}</tspan>'
        else:
            res += f'<tspan class="bl-mid">{esc}</tspan>'
    return res

def generate_duality_svg(output_path: str):
    width = 960
    height = 650
    font_size = 11.8
    line_height = 15.6
    start_y = 75
    text_x = 45

    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg_parts.append("""  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0d12"/>
      <stop offset="100%" stop-color="#05070a"/>
    </linearGradient>
    <linearGradient id="terminal-border" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ff7700" stop-opacity="0.35"/>
      <stop offset="50%" stop-color="#2d3748" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="#1e293b" stop-opacity="0.3"/>
    </linearGradient>
  </defs>""")

    # CSS styles: Left Orange, Right Black / Deep Dark Blue
    svg_parts.append("""  <style>
    .terminal-window {
      fill: url(#bg);
      stroke: url(#terminal-border);
      stroke-width: 1.2;
      rx: 8;
    }
    
    .terminal-tag {
      font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
      font-size: 13.5px;
      font-weight: 600;
      fill: #5a646e;
      letter-spacing: 0.5px;
    }
    
    .prompt-text {
      font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
      font-size: 13.5px;
      font-weight: 600;
    }
    .prompt-user { fill: #00ff66; }
    .prompt-sym { fill: #94a3b8; }
    .cursor {
      fill: #e2e8f0;
      animation: blink 0.9s infinite step-start;
      font-weight: 900;
    }

    .ascii-line {
      font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
      font-size: 11.8px;
      white-space: pre;
    }
    
    /* Left Orange / Amber Palette */
    .or-bright { fill: #ff9d00; font-weight: 700; }
    .or-mid    { fill: #e56b00; }
    .or-dim    { fill: #994400; }
    
    /* Left Eye Reticle - Golden Amber Solar Glow */
    .eye-reticle-or {
      fill: #ffe066;
      font-weight: 900;
      filter: drop-shadow(0 0 3px rgba(255, 170, 0, 0.9));
    }

    /* Center Pipe */
    .pipe {
      fill: #3b424d;
      font-weight: 900;
    }

    /* Right Side: Stealth Black and Deep Midnight Dark Blue */
    .bl-bright { fill: #384556; font-weight: 700; }  /* Dark slate / obsidian steel */
    .bl-mid    { fill: #1c2430; }                    /* Deep midnight shadow */
    .bl-dim    { fill: #121820; }                    /* Stealth near-black */
    
    /* Right Eye Reticle - Deep Stealth Blue / Dark Sapphire */
    .eye-reticle-bl {
      fill: #1d4ed8;
      font-weight: 900;
      filter: drop-shadow(0 0 3px rgba(29, 78, 216, 0.85));
    }

    @keyframes fadeIn {
      0%   { opacity: 0; }
      100% { opacity: 1; }
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

    # Background frame
    svg_parts.append(f'  <rect x="2" y="2" width="{width-4}" height="{height-4}" class="terminal-window" />')

    # Top Left Tag
    svg_parts.append('  <text x="35" y="42" class="terminal-tag">[OCTOCAT // DUALITY // ACTIVE]</text>')

    # ASCII Duality Octocat
    delay = 0.04
    for idx, raw_line in enumerate(RAW_DUALITY_LINES):
        pipe_pos = raw_line.find('|')
        left_txt = raw_line[:pipe_pos]
        pipe_ch = "|"
        right_txt = raw_line[pipe_pos+1:]

        y = start_y + (idx * line_height)
        esc_left = format_left(left_txt, idx)
        esc_pipe = f'<tspan class="pipe">{pipe_ch}</tspan>'
        esc_right = format_right(right_txt, idx)
        
        svg_parts.append(
            f'  <text x="{text_x}" y="{y}" class="ascii-line anim-row" style="animation-delay: {delay:.2f}s;">'
            f'{esc_left}{esc_pipe}{esc_right}'
            f'</text>'
        )
        delay += 0.035

    # Bottom Left Prompt & Bottom Right Tag
    prompt_y = height - 38
    svg_parts.append(
        f'  <text x="35" y="{prompt_y}" class="prompt-text">'
        f'<tspan class="prompt-user">bash-@-kekkan74</tspan> <tspan class="prompt-sym">~ &gt;</tspan> '
        f'<tspan class="cursor">█</tspan>'
        f'</text>'
    )
    svg_parts.append(f'  <text x="{width - 35}" y="{prompt_y}" text-anchor="end" class="terminal-tag">[OCTOCAT // DUALITY // ACTIVE]</text>')

    svg_parts.append('</svg>\n')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
    print(f"[+] Successfully generated Duality SVG with Stealth Black/Dark Blue: {output_path}")

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(out_dir, "octocat-duality.svg")
    generate_duality_svg(target)
