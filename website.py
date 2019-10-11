import django.template
import os.path
import unittest
import markdown


def extractScreenshotShortname(screenshot):
    return os.path.basename(screenshot).split("-")[0]


class TestExtractScreenshotShortname(unittest.TestCase):
    def test_extractScreenshotShortname(self):
        self.assertEqual(extractScreenshotShortname("foo-title.png"), "foo")
        self.assertEqual(extractScreenshotShortname("foo-bar-rtitle.png"), "foo")
        self.assertEqual(extractScreenshotShortname("a/b/c/foo-bar-rtitle.png"), "foo")


def sortScreenshots(played_games, screenshots):
    temp_map = {game["shortname"]: game for game in played_games[:-1]}
    for g in played_games[:-1]:
        g["screenshots"] = []
    for screenshot in screenshots:
        temp_map[extractScreenshotShortname(screenshot)]["screenshots"].append(
            screenshot
        )


class TestSortScreenshots(unittest.TestCase):
    def test_sortScreenshots(self):
        played_games = [{"shortname": "foo"}, {"shortname": "bar"}, {}]
        screenshots = [
            "foo-title.png",
            "bar-credits.png",
            "foo-credits.png",
            "bar-title.png",
        ]
        sortScreenshots(played_games, screenshots)

        self.assertIn("screenshots", played_games[0])
        foo_screenshots = played_games[0]["screenshots"]
        self.assertEqual(len(foo_screenshots), 2)
        self.assertIn("foo-title.png", foo_screenshots)
        self.assertIn("foo-credits.png", foo_screenshots)

        self.assertIn("screenshots", played_games[1])
        bar_screenshots = played_games[1]["screenshots"]
        self.assertEqual(len(bar_screenshots), 2)
        self.assertIn("bar-credits.png", bar_screenshots)
        self.assertIn("bar-title.png", bar_screenshots)


def renderGame(out, template, game, prev=None, next=None):
    game = dict(game)
    shortname = game.get("shortname", False)
    game["next"] = next
    game["prev"] = prev
    if game.get("markdown", False):
        game["notes"] = markdown.markdown(game["notes"])
    context = django.template.Context(game)
    out["docs/" + shortname + ".html"] = template.render(context)


def renderWebsite(games, played_games, full_regen=False):
    out = {}

    engine = django.template.Engine(["resources"], builtins=["filters"])
    template = engine.get_template("templates/lists.html")
    context = django.template.Context(
        {"remaining_games": games, "played_games": played_games}
    )
    out["docs/lists.html"] = template.render(context)

    game_template = engine.get_template("templates/game-page.html")

    if full_regen:
        renderGame(
            out, game_template, played_games[0], next=played_games[1]["shortname"]
        )

        for i in range(1, len(played_games) - 3):
            renderGame(
                out,
                game_template,
                played_games[i],
                played_games[i - 1]["shortname"],
                played_games[i + 1]["shortname"],
            )

    renderGame(
        out,
        game_template,
        played_games[len(played_games) - 3],
        played_games[len(played_games) - 4]["shortname"],
        played_games[len(played_games) - 2]["shortname"],
    )

    renderGame(
        out,
        game_template,
        played_games[len(played_games) - 2],
        prev=played_games[len(played_games) - 3]["shortname"],
    )

    context = django.template.Context({})
    template = engine.get_template("templates/about.html")
    out["docs/about.html"] = template.render(context)

    count = len(played_games) - 1
    percent = int(count / 255 * 100)
    recent = played_games[-11:-1]
    recent.reverse()
    context = django.template.Context(
        {
            "recent_games": recent,
            "next_up": played_games[-1],
            "count": count,
            "percent": percent,
        }
    )
    template = engine.get_template("templates/index.html")
    out["docs/index.html"] = template.render(context)

    return out
