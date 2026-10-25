"""Add up Ludus Points from a list of activity.

Simplified example of the 1.8 rules. In the app, points are counted and
confirmed by the server; this file only shows the arithmetic.
"""
from collections import Counter

WELCOME_BONUS = 100
POINTS = {
    "play_90_minutes": 20,    # every 1h30 spent in Ludus
    "download_finished": 30,
    "game_completed": 60,
    "community_post": 10,     # up to 3 posts a day
    "daily_visit": 5,
}
DAILY_LIMITS = {"community_post": 3, "daily_visit": 1}


def total_points(events, include_welcome=True):
    """events: list of (day, kind) pairs, e.g. ("2026-10-25", "community_post")."""
    per_day = Counter()
    total = WELCOME_BONUS if include_welcome else 0
    for day, kind in events:
        if kind not in POINTS:
            continue
        limit = DAILY_LIMITS.get(kind)
        if limit is not None:
            if per_day[(day, kind)] >= limit:
                continue
            per_day[(day, kind)] += 1
        total += POINTS[kind]
    return total


if __name__ == "__main__":
    week = [
        ("2026-10-20", "daily_visit"), ("2026-10-20", "play_90_minutes"),
        ("2026-10-20", "download_finished"),
        ("2026-10-21", "daily_visit"), ("2026-10-21", "daily_visit"),        # second visit: no points
        ("2026-10-21", "community_post"), ("2026-10-21", "community_post"),
        ("2026-10-21", "community_post"), ("2026-10-21", "community_post"),  # fourth post: no points
        ("2026-10-22", "game_completed"),
    ]
    print("Points after this week:", total_points(week))
