using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using DotLiquid;

namespace P255
{
	[LiquidType("*")]
	public class GamesDataEntry
	{
		[JsonPropertyName("game")]
		public string Game { get; set; }
		[JsonPropertyName("meta-rating")]
		public string MetaRating { get; set; }
		[JsonPropertyName("meta-user")]
		public string MetaUser { get; set; }
		[JsonPropertyName("date")]
		public string Date { get; set; }

		public GamesDataEntry(string game, string metaRating, string metaUser, string date)
		{
			Game = game;
			MetaRating = metaRating;
			MetaUser = metaUser;
			Date = date;
		}
	}
	
	[LiquidType("*")]
	public class PlayedDataEntry
	{
		[JsonPropertyName("game")]
		public string Game { get; set; }
		[JsonPropertyName("meta-rating")]
		public string MetaRating { get; set; }
		[JsonPropertyName("meta-user")]
		public string MetaUser { get; set; }
		[JsonPropertyName("date")]
		public string Date { get; set; }
		[JsonPropertyName("rating")]
		public int Rating { get; set; }
		[JsonPropertyName("shortname")]
		[JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
		public string? Shortname { get; set; }
		[JsonPropertyName("status")]
		[JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
		public string? Status { get; set; }
		[JsonPropertyName("status-note")]
		[JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
		public string? StatusNote { get; set; }
		[JsonPropertyName("notes")]
		[JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
		public string? Notes { get; set; }
		[JsonPropertyName("completion-date")]
		[JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
		public string? CompletionDate { get; set; }
		[JsonPropertyName("markdown")]
		[JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
		public bool? Markdown { get; set; }
		
		public PlayedDataEntry(string game, string metaRating, string metaUser, string date)
		{
			Game = game;
			MetaRating = metaRating;
			MetaUser = metaUser;
			Date = date;
			Rating = -1;
		}
	}
	public static class DataManager
	{
		public static string? GetPlaying()
		{
			var jsonString = File.ReadAllText("played-games.json");
			var entries = JsonSerializer.Deserialize<List<PlayedDataEntry>>(jsonString);
			var last = entries!.Last();
			return last.Rating == -1 ? last.Game : null;
		}

		public static string CycleNextGame()
		{
			var jsonString = File.ReadAllText("games.json");
			var gamesEntries = JsonSerializer.Deserialize<List<GamesDataEntry>>(jsonString);
			var r = new Random(Guid.NewGuid().GetHashCode());
			var selected = r.Next(gamesEntries!.Count);
			var selectedEntry = gamesEntries[selected];
			gamesEntries.RemoveAt(selected);

			var newEntry = new PlayedDataEntry(selectedEntry.Game, selectedEntry.MetaRating, selectedEntry.MetaUser, selectedEntry.Date);

			var jsonString2 = File.ReadAllText("played-games.json");
			var entries = JsonSerializer.Deserialize<List<PlayedDataEntry>>(jsonString2);
			entries!.Add(newEntry);
			
			var options = new JsonSerializerOptions { WriteIndented = true };
			File.WriteAllText("games.json", JsonSerializer.Serialize(gamesEntries, options));
			File.WriteAllText("played-games.json", JsonSerializer.Serialize(entries, options));

			return selectedEntry.Game;
		}

		public static string WriteCompletedGame(
			MainForm.Status status, 
			string statusNote, 
			int rating,
			string notes
		)
		{
			var jsonString = File.ReadAllText("played-games.json");
			var entries = JsonSerializer.Deserialize<List<PlayedDataEntry>>(jsonString);
			var last = entries!.Last();
			
			last.Status = ToJsonStatus(status);
			last.StatusNote = statusNote != "" ? statusNote : null;
			last.Rating = rating;
			last.Notes = notes;
			last.Markdown = true;
			last.Shortname = MakeShortname(last.Game, entries!.Select(e => e.Shortname!).ToList());

			var today = DateTime.Today;
			last.CompletionDate = $"{today.Year}-{today.Month}-{today.Day}";
			
			var options = new JsonSerializerOptions { WriteIndented = true };
			File.WriteAllText("played-games.json", JsonSerializer.Serialize(entries, options));

			return last.Shortname;
		}

		private static string MakeShortname(string lastGame, List<string> allShortnames)
		{
			var shortname = "";
			foreach (var c in lastGame.Split(' ', ':').Where(w => !string.IsNullOrEmpty(w)).Select(w => FilterRoman(w.ToLower()).First()))
			{
				shortname += c;
			}

			if (allShortnames.Contains(shortname))
			{
				var n = 2;
				while (allShortnames.Contains(shortname + $"{n}"))
				{
					n += 1;
				}

				return shortname + $"{n}";
			}

			return shortname;
		}

		private static string FilterRoman(string s)
		{
			switch (s)
			{
				case "ii":
					return "2";
				case "iii":
					return "3";
				case "iv" :
					return "4";
				case "v":
					return "5";
				case "vi":
					return "6";
				case "vii":
					return "7";
				case "viii":
					return "8";
				case "ix":
					return "9";
				case "x":
					return "10";
				case "xi":
					return "11";
				case "xii":
					return "12";
				case "xiii":
					return "13";
				default:
					return s;
			}
		}

		private static string? ToJsonStatus(MainForm.Status status)
		{
			switch (status)
			{
				case MainForm.Status.Complete:
					return "complete";
				case MainForm.Status.Other:
					return "other";
				case MainForm.Status.NotComplete:
					return "not-complete";
				default:
					throw new Exception("Unknown status...");
			}
		}

		public static List<GamesDataEntry> GetGames()
		{
			var jsonString = File.ReadAllText("games.json");
			var entries = JsonSerializer.Deserialize<List<GamesDataEntry>>(jsonString);
			return entries!;
		}

		public static List<PlayedDataEntry> GetPlayedGames()
		{
			var jsonString = File.ReadAllText("played-games.json");
			var entries = JsonSerializer.Deserialize<List<PlayedDataEntry>>(jsonString);
			return entries!;
		}
	}
}
