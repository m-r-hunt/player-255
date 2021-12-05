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
	}
}
