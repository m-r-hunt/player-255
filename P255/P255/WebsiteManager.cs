using System.Diagnostics;
using System.IO;
using System.Linq;
using DotLiquid;
using DotLiquid.FileSystems;

namespace P255
{
	class FS : IFileSystem
	{
		public string ReadTemplateFile(Context context, string templateName)
		{
			return File.ReadAllText(Path.Join("resources", templateName.Replace("\"", "")));
		}
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

			// Generate Lists page
			var listsTemplate = Template.Parse(File.ReadAllText("resources/templates/lists.html"));
			var listsHtml = listsTemplate.Render(Hash.FromAnonymousObject(new
			{
				played_games = playedGames,
				remaining_games = DataManager.GetGames(),
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
				next_up = DataManager.GetPlaying() != null ? playedGames.Last() : null,
				recent_games = playedGames.TakeLast(11).Reverse().TakeLast(10),
			}));
			File.WriteAllText("docs/index.html", indexHtml);

			// Generate game pages
		}
	}
}
