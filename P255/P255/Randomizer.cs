using System;
using System.Collections.Generic;
using System.Linq;

namespace P255;

static class RandomLog
{
	private static bool _verbose = true;
	private static bool _logSpoilers = true;

	public static void Log(string message)
	{
		if (_verbose)
		{
			Console.WriteLine(message);
		}
	}

	public static void LogSpoiler(string message)
	{
		if (_verbose && _logSpoilers)
		{
			Console.WriteLine(message);
		}
	}
}

class Bucket
{
	public int Capacity;
	public List<string> Games;

	public static Random RNG;
	public static void Shuffle(List<string> a)
	{
		for (var i = 1; i < a.Count; i++)
		{
			var j = RNG.Next(0, i+1);
			(a[j], a[i]) = (a[i], a[j]);
		}
	}

	public Bucket(int capacity)
	{
		Capacity = capacity;
		Games = new List<string>(capacity);
	}

	public List<string> Shuffled()
	{
		var a = Games.ToList();
		Shuffle(a);
		return a;
	}

	public bool IsFull() => Games.Count >= Capacity;

	public bool RejectIfFull()
	{
		if (Games.Count >= Capacity)
		{
			RandomLog.Log("Bucket full, rejecting");
			return true;
		}
		return false;
	}
}

class BucketChain
{
	public List<Bucket> Buckets;

	public BucketChain(int games, int bucketCount)
	{
		RandomLog.Log($"BucketChain({games}, {bucketCount})");
		Buckets = new();
		
		var size = games / bucketCount;
		for (int i = 0; i < bucketCount; i++)
		{
			Buckets.Add(new Bucket(size));
		}
		var total = size * bucketCount;
		while (total < games)
		{
			var idx = Bucket.RNG.Next(bucketCount);
			Buckets[idx].Capacity += 1;
			RandomLog.Log($"Expanded Bucket {idx}");
			total += 1;
		}
		
		RandomLog.Log($"Total buckets: {Buckets.Count}");
	}

	public List<string> Flatten()
	{
		var ret = new List<string>();
		foreach (var b in Buckets)
		{
			ret.AddRange(b.Shuffled());
		}
		return ret;
	}
}

public static class Randomizer
{
	private static void AllocateSeries(BucketChain bc, int bucketCount, List<string> series)
	{
		for (var i = 0; i < series.Count; i++)
		{
			var candidateBucketsMin = i * bucketCount / series.Count;
			var candidateBucketsMax = candidateBucketsMin + bucketCount / series.Count;
			if (i > 0)
			{
				candidateBucketsMin += 1;
			}
			if (candidateBucketsMax <= candidateBucketsMin)
			{
				throw new Exception("Nowhere to go");
			}
			RandomLog.Log($"Series game {series[i]} to go in bucket [{candidateBucketsMin}-{candidateBucketsMax})");
			var idx = -1;
			do
			{
				idx = Bucket.RNG.Next(candidateBucketsMin, candidateBucketsMax);
			} while (bc.Buckets[idx].RejectIfFull());
			bc.Buckets[idx].Games.Add(series[i]);
			RandomLog.LogSpoiler($"Adding series game {series[i]} to bucket {idx}");
		}
	}
	
	public static List<String> GetRandomOrder()
	{
		var data = DataManager.GetData();

		Bucket.RNG = new Random(data.Seed);

		var bucketCount = 1;
		foreach (var series in data.OrderedSeries)
		{
			bucketCount = LCM(bucketCount, series.Count);
		}
		foreach (var series in data.UnorderedSeries)
		{
			bucketCount = LCM(bucketCount, series.Count);
		}
		RandomLog.Log($"bucketCount: {bucketCount}");
		
		var bc = new BucketChain(data.Games.Count - 2, bucketCount);

		foreach (var series in data.OrderedSeries)
		{
			AllocateSeries(bc, bucketCount, series);
		}
		foreach (var series in data.UnorderedSeries)
		{
			var shuffled = series.ToList();
			Bucket.Shuffle(shuffled);
			AllocateSeries(bc, bucketCount, shuffled);
		}
		
		var games = data.Games.Where(g => g.Game != data.FirstGame && g.Game != data.LastGame).Select(g => g.Game).ToList();
		Bucket.Shuffle(games);
		var i = 0;
		foreach (var b in bc.Buckets)
		{
			while (!b.IsFull())
			{
				while (data.OrderedSeries.Any(s =>
				       s.Contains(games[i]) || data.UnorderedSeries.Any(s => s.Contains(games[i]))))
				{
					i++;
				}
				b.Games.Add(games[i]);
				i++;
			}
		}
		var ret = new List<string> {data.FirstGame};
		ret.AddRange(bc.Flatten());
		ret.Add(data.LastGame);
		
		// Sanity checks
		if (ret.Count != data.Games.Count)
		{
			throw new Exception("Randomizing failed somehow?");
		}
		if (!data.Games.All(g => ret.Contains(g.Game)))
		{
			foreach (var g in data.Games)
			{
				if (!ret.Contains(g.Game))
				{
					Console.WriteLine($"Missing {g.Game}");
				}
			}
			foreach (var g in ret)
			{
				Console.WriteLine($"{g}");
			}
			throw new Exception($"Randomizing failed somehow? {data.Games.Where(g => ret.Contains(g.Game)).First().Game}");
		}
		
		return ret;
	}
	
	static int GCF(int a, int b)
	{
		while (b != 0)
		{
			int temp = b;
			b = a % b;
			a = temp;
		}
		return a;
	}

	static int LCM(int a, int b)
	{
		return (a / GCF(a, b)) * b;
	}
}
