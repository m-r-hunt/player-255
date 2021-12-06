using System;
using Eto.Forms;

namespace P255.Gtk;

class Program
{
	[STAThread]
	public static void Main(string[] args)
	{
		new Application(Eto.Platforms.Gtk).Run(new MainForm());
	}
}
