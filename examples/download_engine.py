"""Pick a download engine for a link.

Simplified example. Ludus 1.8 has engines for torrents, direct links and
file hosts, plus "Ready to play", which installs the game after downloading.
Only the choice is shown here; nothing is downloaded.
"""
from urllib.parse import urlparse

# Hosts that work best with several parallel connections.
FILE_HOSTS = {"files.example", "share.example"}


def choose_engine(link, install_after=False):
    if install_after:
        return "ready-to-play"
    if link.startswith("magnet:") or link.endswith(".torrent"):
        return "torrent"
    host = urlparse(link).hostname or ""
    if host in FILE_HOSTS:
        return "turbo"
    if link.startswith(("http://", "https://")):
        return "direct"
    raise ValueError("Unsupported link: " + link)


if __name__ == "__main__":
    samples = [
        ("magnet:?xt=urn:btih:0000000000000000000000000000000000000000", False),
        ("https://files.example/abc123", False),
        ("https://mirror.example/game-setup.zip", False),
        ("https://mirror.example/game-setup.zip", True),
    ]
    for link, install in samples:
        print(f"{choose_engine(link, install):14} {link}")
