﻿using System.Diagnostics;
using System.IO;
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

			// Generate Lists page
			var listsTemplate = Template.Parse(File.ReadAllText("resources/templates/lists.html"));
			var listsHtml = listsTemplate.Render(Hash.FromAnonymousObject(new
			{
				played_games = DataManager.GetPlayedGames(),
				remaining_games = DataManager.GetGames()
			}));
			File.WriteAllText("docs/lists.html", listsHtml);

			// Generate about page
			var aboutTemplate = Template.Parse(File.ReadAllText("resources/templates/about.html"));
			var aboutHtml = aboutTemplate.Render(Hash.FromAnonymousObject(new
			{
				played_games = DataManager.GetPlayedGames(),
				remaining_games = DataManager.GetGames()
			}));
			File.WriteAllText("docs/about.html", aboutHtml);

			// Generate index page

			// Generate game pages
		}
	}
}
