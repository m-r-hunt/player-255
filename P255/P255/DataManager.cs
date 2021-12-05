using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace P255
{
	public class DataEntry
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
		public string? Shortname { get; set; }
		[JsonPropertyName("status")]
		public string? Status { get; set; }
		[JsonPropertyName("status-note")]
		public string? StatusNote { get; set; }
		[JsonPropertyName("notes")]
		public string? Notes { get; set; }
		[JsonPropertyName("completion-date")]
		public string? CompletionDate { get; set; }
		[JsonPropertyName("markdown")]
		public bool? Markdown { get; set; }
	}
	public static class DataManager
	{
		public static string? GetPlaying()
		{
			var jsonString = File.ReadAllText("played-games.json");
			var entries = JsonSerializer.Deserialize<List<DataEntry>>(jsonString);
			var last = entries.Last();
			return last.Rating == -1 ? last.Game : null;
		}

		public static void WriteCompletedGame(
			MainForm.Status status, 
			string statusNote, 
			int rating,
			string notes
		)
		{
			var jsonString = File.ReadAllText("played-games.json");
			var entries = JsonSerializer.Deserialize<List<DataEntry>>(jsonString);
			var last = entries.Last();
			
			last.Status = ToJsonStatus(status);
			last.StatusNote = statusNote != "" ? statusNote : null;
			last.Rating = rating;
			last.Notes = notes;
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
	}
}
