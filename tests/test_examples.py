import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples"))

import download_engine  # noqa: E402
import ludus_points  # noqa: E402
import name_matching  # noqa: E402
import save_backups  # noqa: E402
import theme_to_css  # noqa: E402


class ExamplesTest(unittest.TestCase):
    def test_contrast_ratio_extremes(self):
        self.assertAlmostEqual(theme_to_css.contrast_ratio("#000000", "#ffffff"), 21.0, places=1)
        self.assertAlmostEqual(theme_to_css.contrast_ratio("#777777", "#777777"), 1.0, places=2)

    def test_theme_has_every_variable(self):
        css = theme_to_css.theme_to_css({"background": "#101010", "text": "#ffffff", "accent": "#ff0000"})
        for name in ("--bg", "--surface", "--border", "--text", "--accent", "--radius"):
            self.assertIn(name, css)

    def test_points_respect_daily_limits(self):
        posts = [("2026-10-25", "community_post")] * 5
        self.assertEqual(ludus_points.total_points(posts, include_welcome=False), 30)
        self.assertEqual(ludus_points.total_points([]), 100)

    def test_matching_requires_the_same_sequel(self):
        self.assertEqual(name_matching.score("Example Quest II", "Example Quest III"), 0.0)
        self.assertGreater(name_matching.score("Example Quest II", "Example Quest 2 + 3 DLCs"), 0.9)

    def test_engine_choice(self):
        self.assertEqual(download_engine.choose_engine("magnet:?xt=urn:btih:00"), "torrent")
        self.assertEqual(download_engine.choose_engine("https://files.example/a"), "turbo")
        self.assertEqual(download_engine.choose_engine("https://a.example/b", install_after=True), "ready-to-play")
        with self.assertRaises(ValueError):
            download_engine.choose_engine("ftp://a.example/b")

    def test_keeps_five_backups_per_game(self):
        items = [save_backups.Backup("g", f"2026-10-{d:02d}", 1) for d in range(1, 9)]
        self.assertEqual(len(save_backups.backups_to_delete(items)), 3)


if __name__ == "__main__":
    unittest.main()
