using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using DotLiquid;

namespace P255;

public class P255Data
{
	[JsonPropertyName("seed")] public int Seed{ get; set; }
	[JsonPropertyName("first_game")] public string FirstGame{ get; set; }
	[JsonPropertyName("last_game")] public string LastGame{ get; set; }
	[JsonPropertyName("now_playing")] public string NowPlaying{ get; set; }
	[JsonPropertyName("ordered_series")] public List<List<string>> OrderedSeries{ get; set; }
	[JsonPropertyName("unordered_series")] public List<List<string>> UnorderedSeries{ get; set; }
	[JsonPropertyName("played_games")] public List<PlayedDataEntry> PlayedGames{ get; set; }
	[JsonPropertyName("games")] public List<GamesDataEntry> Games{ get; set; }
}

[LiquidType("*")]
public class GamesDataEntry
{
	[JsonPropertyName("game")]
	public string Game { get; set; }
	[JsonPropertyName("meta-rating")]
	public int MetaRating { get; set; }
	[JsonPropertyName("meta-user")]
	public string MetaUser { get; set; }
	[JsonPropertyName("date")]
	public string Date { get; set; }

	public GamesDataEntry(string game, int metaRating, string metaUser, string date)
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
	public int MetaRating { get; set; }
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
		
	public PlayedDataEntry(string game, int metaRating, string metaUser, string date)
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
	private static P255Data? _data;
	
	public static P255Data GetData()
	{
		if (_data == null)
		{
			var jsonString = File.ReadAllText("p255.json");
			_data = JsonSerializer.Deserialize<P255Data>(jsonString)!;
		}
		return _data;
	}

	private static void WriteData()
	{
		var options = new JsonSerializerOptions { WriteIndented = true };
		File.WriteAllText("p255.json", JsonSerializer.Serialize(_data, options));
	}
	
	public static string? GetPlaying()
	{
		var data = GetData();
		return data.NowPlaying;
	}

	public static string CycleNextGame()
	{
		var data = GetData();
		
		var order = Randomizer.GetRandomOrder();
		
		// Sanity Checks
		int i = 0;
		for (i = 0; i < data.PlayedGames.Count; i++)
		{
			if (data.PlayedGames[i].Game != order[i])
			{
				throw new Exception("Existing played game order doesn't match randomzied order");
			}
		}
		if (data.NowPlaying != order[i])
		{
			throw new Exception("Existing played game order doesn't match randomzied order");
		}

		var e = data.Games.First(ee => ee.Game == data.NowPlaying);
		
		var newEntry = new PlayedDataEntry(e.Game, e.MetaRating, e.MetaUser, e.Date);
		data.PlayedGames.Add(newEntry);

		i += 1;
		if (i >= order.Count)
		{
			data.NowPlaying = "Challenge Finished!";
		}
		else
		{
			data.NowPlaying = order[i];
		}
		
		WriteData();
		return data.NowPlaying;
	}

	public static string WriteCompletedGame(
	MainForm.Status status, 
	string statusNote, 
	int rating,
	string notes
	)
	{
		var data = GetData();
		var last = data.PlayedGames.Last();
			
		last.Status = ToJsonStatus(status);
		last.StatusNote = statusNote != "" ? statusNote : null;
		last.Rating = rating;
		last.Notes = notes;
		last.Markdown = true;
		last.Shortname = MakeShortname(last.Game, data.PlayedGames.Select(e => e.Shortname!).ToList());

		var today = DateTime.Today;
		last.CompletionDate = $"{today.Year}-{today.Month}-{today.Day}";

		WriteData();

		return last.Shortname;
	}

	private static string MakeShortname(string lastGame, List<string> allShortnames)
	{
		var shortname = "";
		foreach (var c in lastGame.Split(' ', ':', '\'').Where(w => !string.IsNullOrEmpty(w)).Select(w => FilterRoman(w.ToLower()).First()))
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

	public static List<GamesDataEntry> GetUnplayedGames()
	{
		var data = GetData();
		return data.Games.Where(e => data.PlayedGames.All(ee => ee.Game != e.Game) && e.Game != data.NowPlaying).ToList();
	}

	public static List<PlayedDataEntry> GetPlayedGames()
	{
		var data = GetData();
		return data.PlayedGames;
	}

	public static int GetTotalGames()
	{
		return GetData().Games.Count;
	}
}
