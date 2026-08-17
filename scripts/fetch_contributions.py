import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Jatin2705"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path("data/contributions.json")


def level_from_class(classes):
    for cls in classes:
        match = re.fullmatch(r"ContributionCalendar-day", cls)
        if match:
            continue
        match = re.search(r"(?:level-|contribution-level-)(\d)", cls)
        if match:
            return int(match.group(1))
    return 0


def main():
    response = requests.get(
        URL,
        headers={"User-Agent": "Jatin2705-profile-art/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    days = []
    for cell in soup.select("td.ContributionCalendar-day[data-date], [data-date].ContributionCalendar-day"):
        raw_date = cell.get("data-date")
        if not raw_date:
            continue
        try:
            day = date.fromisoformat(raw_date)
        except ValueError:
            continue
        label = cell.get("aria-label", "")
        count_match = re.search(r"(\d[\d,]*) contribution", label)
        count = int(count_match.group(1).replace(",", "")) if count_match else 0
        level = level_from_class(cell.get("class", []))
        days.append({"date": raw_date, "count": count, "level": level})

    # Fallback for GitHub markup changes: parse the text labels even if classes move.
    if not days:
        for cell in soup.select("[data-date]"):
            raw_date = cell.get("data-date")
            try:
                date.fromisoformat(raw_date)
            except (TypeError, ValueError):
                continue
            label = cell.get("aria-label", "")
            match = re.search(r"(\d[\d,]*) contribution", label)
            days.append({"date": raw_date, "count": int(match.group(1).replace(",", "")) if match else 0, "level": 0})

    days = sorted({item["date"]: item for item in days}.values(), key=lambda x: x["date"])
    counts = [item["count"] for item in days]

    current_streak = 0
    longest_streak = 0
    streak = 0
    for item in days:
        if item["count"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0

    for item in reversed(days):
        if item["count"] > 0:
            current_streak += 1
        else:
            break

    monthly = Counter(item["date"][:7] for item in days)
    monthly_totals = {}
    for item in days:
        monthly_totals.setdefault(item["date"][:7], 0)
        monthly_totals[item["date"][:7]] += item["count"]

    payload = {
        "username": USERNAME,
        "updated_at": date.today().isoformat(),
        "days": days,
        "stats": {
            "contributions": sum(counts),
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "best_day": max(days, key=lambda x: x["count"], default={"date": None, "count": 0}),
            "monthly_totals": monthly_totals,
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(days)} days to {OUT}")


if __name__ == "__main__":
    main()
