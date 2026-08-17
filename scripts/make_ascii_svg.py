from pathlib import Path
import numpy as np
from PIL import Image

INPUT = Path("source-prepped.png")
OUTPUT = Path("avi-ascii.svg")
RAMP = " .`:-=+*cs#%@"
COLS, ROWS = 54, 25
WIDTH, HEIGHT = 370, 330


def main():
    if not INPUT.exists():
        raise SystemExit(f"Missing {INPUT}. Run prep_photo.py first.")

    image = Image.open(INPUT).convert("L")
    ratio = image.height / image.width
    target_h = int(COLS * ratio * 0.5)
    target_h = max(1, min(ROWS, target_h))
    image = image.resize((COLS, target_h), Image.Resampling.LANCZOS)
    pixels = np.asarray(image)

    lines = []
    for row in pixels:
        chars = "".join(RAMP[min(len(RAMP)-1, int(v) * (len(RAMP)-1) // 256)] for v in row)
        lines.append(chars)

    y0 = 48
    dy = 10
    text_nodes = []
    for i, line in enumerate(lines):
        delay = 0.10 + i * 0.06
        text_nodes.append(
            f'<text class="row r{i}" x="185" y="{y0 + i*dy}">{line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</text>'
        )

    style_rows = "".join(f".r{i}{{animation-delay:{0.10+i*0.06:.2f}s}}" for i in range(len(lines)))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<style>
 text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:6px; fill:#c9d1d9; letter-spacing:0; }}
 .row {{ opacity:0; animation: reveal .28s ease forwards; }}
 {style_rows}
 @keyframes reveal {{ from {{ opacity:0; transform:translateX(-10px) }} to {{ opacity:1; transform:translateX(0) }} }}
</style>
<rect width="370" height="330" rx="12" fill="#0d1117" stroke="#30363d"/>
<text x="16" y="25" font-size="12" fill="#58a6ff">jatin@github ~ $ cat portrait.txt</text>
<g text-anchor="middle">{''.join(text_nodes)}</g>
<text x="185" y="310" text-anchor="middle" font-size="11" fill="#39d353">$ portrait loaded successfully</text>
</svg>'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
