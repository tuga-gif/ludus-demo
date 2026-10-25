"""Match a game title against release names from different sources.

Simplified example. Release names come with extra words ("+ 5 DLCs",
"Free Download", "v1.2"), Roman numerals and years. Normalising both sides
before comparing finds the right release more often.
"""
import re
from difflib import SequenceMatcher

ROMAN = {"ii": "2", "iii": "3", "iv": "4", "v": "5", "vi": "6",
         "vii": "7", "viii": "8", "ix": "9", "x": "10"}
NOISE = [
    r"\+\s*\d*\s*dlcs?.*$",       # "+ 5 DLCs ..."
    r"\bfree download\b",
    r"\b(repack|goty)\b",
    r"[-–]\s*v?\d+(\.\d+)+.*$",    # "- v1.2.3"
    r"\(\d{4}\)",                  # "(2023)"
]


def normalise(title):
    text = title.lower()
    for pattern in NOISE:
        text = re.sub(pattern, " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(ROMAN.get(word, word) for word in text.split())


def score(wanted, candidate):
    """0.0 to 1.0. The sequel number has to be the same."""
    a, b = normalise(wanted), normalise(candidate)
    if set(re.findall(r"\b\d+\b", a)) != set(re.findall(r"\b\d+\b", b)):
        return 0.0
    return round(SequenceMatcher(None, a, b).ratio(), 2)


if __name__ == "__main__":
    wanted = "Example Quest II"
    releases = [
        "Example Quest 2 + 3 DLCs [Repack]",
        "Example Quest III - v1.0.4",
        "Example Quest: Origins (2024)",
        "Example Quest II Free Download",
    ]
    ranked = sorted(((score(wanted, r), r) for r in releases), reverse=True)
    for value, name in ranked:
        print(f"{value:.2f}  {name}")
