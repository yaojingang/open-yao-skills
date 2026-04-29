#!/usr/bin/env python3
"""Capture SVG chapter visuals as PNG files with a headless browser."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def find_browser() -> str:
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for candidate in candidates:
        if os.access(candidate, os.X_OK):
            return candidate

    for name in ["google-chrome", "chromium", "chromium-browser", "msedge", "brave"]:
        path = shutil.which(name)
        if path:
            return path

    raise SystemExit("Missing screenshot browser: install Google Chrome, Microsoft Edge, Brave, or Chromium.")


def capture_svg(browser: str, svg_file: Path, png_file: Path, width: int, height: int, scale: float) -> None:
    svg = svg_file.read_text(encoding="utf-8")
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    html, body {{
      width: {width}px;
      height: {height}px;
      margin: 0;
      overflow: hidden;
      background: #f5f4ed;
    }}
    svg {{
      display: block;
      width: {width}px;
      height: {height}px;
    }}
  </style>
</head>
<body>
{svg}
</body>
</html>
"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        html_file = Path(tmp_dir) / f"{svg_file.stem}.html"
        html_file.write_text(html, encoding="utf-8")
        raw_png = Path(tmp_dir) / f"{svg_file.stem}.raw.png"
        # Chrome on macOS can treat --window-size as an outer window size, which leaves
        # less vertical viewport than requested. Capture taller, then crop to the SVG.
        capture_height = height + 96
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--run-all-compositor-stages-before-draw",
            f"--window-size={width},{capture_height}",
            f"--force-device-scale-factor={scale}",
            f"--screenshot={raw_png}",
            html_file.resolve().as_uri(),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        crop_png(raw_png, png_file, width, height, scale)


def crop_png(source: Path, target: Path, width: int, height: int, scale: float) -> None:
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("Missing Pillow: install the Python PIL/Pillow package to crop browser screenshots exactly.")

    expected_width = int(round(width * scale))
    expected_height = int(round(height * scale))
    with Image.open(source) as image:
        cropped = image.crop((0, 0, expected_width, expected_height))
        cropped.save(target)


def svg_dimensions(svg_file: Path) -> tuple[int, int]:
    head = svg_file.read_text(encoding="utf-8", errors="ignore")[:1200]
    width_match = re.search(r'\bwidth="([0-9.]+)"', head)
    height_match = re.search(r'\bheight="([0-9.]+)"', head)
    if width_match and height_match:
        return int(float(width_match.group(1))), int(float(height_match.group(1)))
    viewbox_match = re.search(r'\bviewBox="[^"]*?\s([0-9.]+)\s([0-9.]+)"', head)
    if viewbox_match:
        return int(float(viewbox_match.group(1))), int(float(viewbox_match.group(2)))
    return 1200, 675


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture SVG visuals to PNG files.")
    parser.add_argument("visuals_dir", help="Directory containing generated SVG files.")
    parser.add_argument("output_dir", help="Directory for PNG screenshots.")
    parser.add_argument("--width", type=int, default=0, help="Screenshot viewport width. Defaults to each SVG width.")
    parser.add_argument("--height", type=int, default=0, help="Screenshot viewport height. Defaults to each SVG height.")
    parser.add_argument("--scale", type=float, default=2.0, help="Device scale factor for crisper screenshots.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    visuals_dir = Path(args.visuals_dir).resolve()
    if not visuals_dir.exists():
        raise SystemExit(f"Visuals directory not found: {visuals_dir}")

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    svg_files = sorted(path for path in visuals_dir.glob("*.svg") if path.is_file())
    if not svg_files:
        raise SystemExit(f"No SVG files found in: {visuals_dir}")

    browser = find_browser()
    for svg_file in svg_files:
        intrinsic_width, intrinsic_height = svg_dimensions(svg_file)
        width = args.width or intrinsic_width
        height = args.height or intrinsic_height
        png_file = output_dir / f"{svg_file.stem}.png"
        capture_svg(browser, svg_file, png_file, width, height, args.scale)
        print(f"- {png_file}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}: {exc.cmd}", file=sys.stderr)
        raise SystemExit(exc.returncode)
