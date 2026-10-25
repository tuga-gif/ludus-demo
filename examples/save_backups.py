"""Keep only the most recent save backups for each game.

Simplified example of the "Automatic save backup" extension: when a game
closes, Ludus stores a compressed copy of its save folder and keeps the five
most recent copies per game.
"""
from collections import defaultdict
from dataclasses import dataclass

KEEP_PER_GAME = 5


@dataclass(frozen=True)
class Backup:
    game: str
    created: str    # ISO date and time
    size_kb: int


def backups_to_delete(backups, keep=KEEP_PER_GAME):
    by_game = defaultdict(list)
    for backup in backups:
        by_game[backup.game].append(backup)
    old = []
    for items in by_game.values():
        items.sort(key=lambda b: b.created, reverse=True)
        old.extend(items[keep:])
    return old


if __name__ == "__main__":
    history = [Backup("example-quest", f"2026-10-{day:02d}T20:00", 900 + day) for day in range(10, 18)]
    history.append(Backup("tiny-racer", "2026-10-15T18:30", 120))
    for backup in backups_to_delete(history):
        print("delete", backup.game, backup.created)
