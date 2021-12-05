using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;

namespace P255
{
	public class ScreenshotManager
	{
		public static void CopyScreenshots(ObservableCollection<MainForm.ScreenshotItem> screenshots, string shortname)
		{
			foreach (var s in screenshots)
			{
				File.Copy(s.ImagePath, Path.Join(".", "static-assets", "images", "screenshots", $"{shortname}-{s.Title}.png")); 
			}
		}

		public static List<string> GetScreenshots(string shortname)
		{
			var others = new List<string>();
			var title = "";
			var credits = "";
			foreach (var f in Directory.EnumerateFiles(Path.Join(".", "static-assets", "images", "screenshots")))
			{
				if (Path.GetFileName(f).StartsWith(shortname))
				{
					if (Path.GetFileName(f).Contains("-title.png"))
					{
						title = Path.GetFileName(f);
					} else if (Path.GetFileName(f).Contains("-credits.png"))
					{
						credits = Path.GetFileName(f);
					}
					else
					{
						others.Add(Path.GetFileName(f));
					}
				}
			}

			var ret = new List<string>();
			ret.Add(title);
			ret.AddRange(others);
			if (!string.IsNullOrEmpty(credits))
			{
				ret.Add(credits);
			}
			return ret;
		}
	}
}
