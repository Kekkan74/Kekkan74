#!/usr/bin/env python3
"""
prep_photo.py
Converts an image (photo or avatar) into high-contrast monochrome ASCII art.
Supports local images, auto-downloading GitHub avatar, contrast enhancement,
and custom ASCII ramps.
Saves the raw text to data/profile_ascii.txt.
"""

import os
import sys
import requests
from PIL import Image, ImageEnhance, ImageOps

ASCII_RAMPS = {
    "standard": " .:-=+*#%@@",
    "cyber": " .:+*#%@",
    "blocks": " ░▒▓█",
    "detailed": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
}

def load_image(input_source: str) -> Image.Image:
    if input_source.startswith("http://") or input_source.startswith("https://"):
        print(f"[*] Downloading image from URL: {input_source}")
        resp = requests.get(input_source, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()
        import io
        return Image.open(io.BytesIO(resp.content))
    
    if os.path.exists(input_source):
        return Image.open(input_source)
    
    raise FileNotFoundError(f"Image source not found: {input_source}")

def image_to_ascii(
    image: Image.Image,
    target_width: int = 60,
    contrast_factor: float = 1.7,
    ramp_name: str = "standard",
    invert: bool = True
) -> list[str]:
    # Convert to grayscale
    gray = image.convert("L")

    # Enhance contrast
    if contrast_factor != 1.0:
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(contrast_factor)

    # Invert for dark terminal background: bright subject pixels become dense ASCII chars
    if invert:
        gray = ImageOps.invert(gray)

    # Monospace font aspect ratio correction (~0.52 to 0.55 height per width)
    orig_w, orig_h = gray.size
    aspect_ratio = orig_h / orig_w
    target_height = int(target_width * aspect_ratio * 0.52)

    resized = gray.resize((target_width, target_height), Image.Resampling.LANCZOS)

    chars = ASCII_RAMPS.get(ramp_name, ASCII_RAMPS["standard"])
    num_chars = len(chars)

    lines = []
    for y in range(target_height):
        line = ""
        for x in range(target_width):
            pixel = resized.getpixel((x, y))
            idx = int((pixel / 255.0) * (num_chars - 1))
            line += chars[idx]
        lines.append(line.rstrip())

    # Trim empty leading/trailing lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    return lines

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_avatar = os.path.join(base_dir, "data", "avatar.jpg")
    default_out = os.path.join(base_dir, "data", "profile_ascii.txt")

    source = sys.argv[1] if len(sys.argv) > 1 else default_avatar
    target_width = int(sys.argv[2]) if len(sys.argv) > 2 else 62
    output_txt = sys.argv[3] if len(sys.argv) > 3 else default_out

    # Fallback to downloading GitHub avatar if local avatar doesn't exist
    if not os.path.exists(source) and not source.startswith("http"):
        print(f"[*] Local image '{source}' not found. Fetching GitHub avatar...")
        source = "https://github.com/Kekkan74.png"

    img = load_image(source)
    print(f"[*] Processing image ({img.size[0]}x{img.size[1]}, format: {img.format or 'JPEG'})...")
    
    ascii_lines = image_to_ascii(img, target_width=target_width, ramp_name="standard", invert=True)

    os.makedirs(os.path.dirname(output_txt), exist_ok=True)
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(ascii_lines) + "\n")

    print(f"[+] Successfully converted to ASCII: {output_txt}")
    print(f"    Dimensions: {target_width} cols x {len(ascii_lines)} lines")

if __name__ == "__main__":
    main()

