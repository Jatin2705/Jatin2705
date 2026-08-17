import json
from pathlib import Path

DATA = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]


def main():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    days = payload.get("days", [])[-371:]
    stats = payload.get("stats", {})

    while len(days) < 371:
        days.insert(0, {"date": "", "count": 0, "level": 0})

    width, height = 860, 205
    left, top = 24, 32
    cell, gap = 11, 3
    step = cell + gap

    rects = []
    for i, item in enumerate(days):
        week = i // 7
        dow = i % 7
        x = left + week * step
        y = top + dow * step
        level = max(0, min(5, int(item.get("level", 0))))
        count = int(item.get("count", 0))
        delay = (week * 0.025) + (dow * 0.018)
        rects.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{PALETTE[level]}" opacity="0" data-date="{item.get("date", "")}" data-count="{count}">' 
            f'<animate attributeName="opacity" from="0" to="1" dur="0.35s" begin="{delay:.3f}s" fill="freeze" />'
            f'</rect>'
        )

    total = stats.get("contributions", 0)
    current = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
 text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
 .fade {{ opacity:0; animation: fade .5s ease forwards; }}
 @keyframes fade {{ to {{ opacity:1 }} }}
</style>
<rect x="1" y="1" width="858" height="203" rx="12" fill="#0d1117" stroke="#30363d"/>
<text x="24" y="21" font-size="12" fill="#8b949e">GitHub contributions • {payload.get("username", "Jatin2705")}</text>
{''.join(rects)}
<g class="fade" style="animation-delay:1.8s">
  <text x="24" y="125" font-size="11" fill="#8b949e">Less</text>
  <rect x="57" y="116" width="11" height="11" rx="2" fill="{PALETTE[0]}"/><rect x="73" y="116" width="11" height="11" rx="2" fill="{PALETTE[1]}"/><rect x="89" y="116" width="11" height="11" rx="2" fill="{PALETTE[2]}"/><rect x="105" y="116" width="11" height="11" rx="2" fill="{PALETTE[3]}"/><rect x="121" y="116" width="11" height="11" rx="2" fill="{PALETTE[4]}"/><rect x="137" y="116" width="11" height="11" rx="2" fill="{PALETTE[5]}"/>
  <text x="156" y="125" font-size="11" fill="#8b949e">More</text>
  <text x="24" y="153" font-size="12" fill="#c9d1d9">{total:,} contributions in the displayed period</text>
  <text x="24" y="174" font-size="11" fill="#8b949e">Current streak: {current} days   •   Longest streak: {longest} days</text>
</g>
</svg>'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
