using System.Diagnostics;
using System.IO;

namespace P255
{
	public static class WebsiteManager
	{
		public static void GenerateWebsite()
		{
			// Robocopy static assets
			// N.b. If we ever actually want to run on another platform, we'll have to use appropriate fast copy method
			// rsync?
			Process.Start(new ProcessStartInfo("robocopy", @"/e .\static-assets .\docs"){CreateNoWindow = true});

			// Generate Lists page

			// Generate game pages

			// Generate about page

			// Generate index page
		}
	}
}
