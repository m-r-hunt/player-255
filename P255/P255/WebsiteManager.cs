using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using DotLiquid;
using DotLiquid.FileSystems;
using Markdig;

namespace P255;

class FS : IFileSystem
{
	public string ReadTemplateFile(Context context, string templateName)
	{
		return File.ReadAllText(Path.Join("resources", templateName.Replace("\"", "")));
	}
}

class GamePageEntry
{
	public string? game { get; set; }
	public string? meta_rating { get; set; }
	public string? meta_user { get; set; }
	public string? date { get; set; }
	public int rating { get; set; }
	public string? shortname { get; set; }
	public string? status { get; set; }
	public string? status_note { get; set; }
	public string? notes { get; set; }
	public string? completion_date { get; set; }
	public bool? markdown { get; set; }
	public string? prev { get; set; }
	public string? next { get; set; }
	public List<string>? screenshots { get; set; }
}
	
public static class WebsiteManager
{
	public static void GenerateWebsite()
	{
		// Robocopy static assets
		// N.b. If we ever actually want to run on another platform, we'll have to use appropriate fast copy method
		// rsync?
		Process.Start(new ProcessStartInfo("robocopy", @"/e .\static-assets .\docs"){CreateNoWindow = true});
			
		// Set up DotLiquid
		Template.FileSystem = new FS();

		var playedGames = DataManager.GetPlayedGames();
		var remainingGames = DataManager.GetGames();
		var isPlaying = DataManager.GetPlaying() != null;

		// Generate Lists page
		var listsTemplate = Template.Parse(File.ReadAllText("resources/templates/lists.html"));
		var listsHtml = listsTemplate.Render(Hash.FromAnonymousObject(new
		{
			played_games = isPlaying ? playedGames.Take(playedGames.Count-1).ToList() : playedGames,
			remaining_games = remainingGames,
			playing = isPlaying ? playedGames.Last() : null,
		}));
		File.WriteAllText("docs/lists.html", listsHtml);

		// Generate about page
		var aboutTemplate = Template.Parse(File.ReadAllText("resources/templates/about.html"));
		var aboutHtml = aboutTemplate.Render(Hash.FromAnonymousObject(new{}));
		File.WriteAllText("docs/about.html", aboutHtml);

		// Generate index page
		var indexTemplate = Template.Parse(File.ReadAllText("resources/templates/index.html"));
		var indexHtml = indexTemplate.Render(Hash.FromAnonymousObject(new
		{
			percent = (playedGames.Count - 1) * 100 / 255,
			count = playedGames.Count - 1,
			next_up = isPlaying ? playedGames.Last() : null,
			recent_games = playedGames.TakeLast(11).Reverse().TakeLast(10),
		}));
		File.WriteAllText("docs/index.html", indexHtml);

		// Generate game pages
		var gameTemplate = Template.Parse(File.ReadAllText("resources/templates/game-page.html"));
		for (var i = 0; i < (isPlaying ? playedGames.Count-1 : playedGames.Count); i++)
		{
			var og = playedGames[i];
			var g = new GamePageEntry()
			{
				completion_date = og.CompletionDate,
				date = og.Date,
				game = og.Game,
				markdown = og.Markdown,
				meta_rating = og.MetaRating,
				meta_user = og.MetaUser,
				notes = og.Notes,
				rating = og.Rating,
				shortname = og.Shortname,
				status = og.Status,
				status_note = og.StatusNote,
				screenshots = ScreenshotManager.GetScreenshots(og.Shortname!),
			};
			if (g.markdown ?? false)
			{
				g.notes = Markdown.ToHtml(g.notes!);
			}

			if (i > 0)
			{
				g.prev = playedGames[i - 1].Shortname;
			}

			if ((isPlaying && i < playedGames.Count - 2) || (!isPlaying && i < playedGames.Count - 1))
			{
				g.next = playedGames[i + 1].Shortname;
			}
			var gameHtml = gameTemplate.Render(Hash.FromAnonymousObject(g));
			File.WriteAllText($"docs/{g.shortname}.html", gameHtml);
		}
	}
}
