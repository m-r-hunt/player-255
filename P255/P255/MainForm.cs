using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using DotLiquid;
using Eto.Forms;
using Eto.Drawing;

namespace P255;

public sealed class MainForm : Form
{
	public enum Status
	{
		Complete,
		NotComplete,
		Other,
	};

	public class ScreenshotItem
	{
		public string ImagePath { get; set; }
		public string Title { get; set; }

		public ScreenshotItem()
		{
			ImagePath = "";
			Title = "";
		}
	}

	private Label PlayingLabel;
	private EnumDropDown<Status> StatusDropDown;
	private TextBox StatusText;
	private List<RadioButton> StarButtons;
	private ObservableCollection<ScreenshotItem> Screenshots;
	private TextArea NotesText;
	private Button SubmitButton;
		
	public MainForm()
	{
		var data = Randomizer.GetRandomOrder();
		
		Title = "Player 255";
		MinimumSize = new Size(700, 800);

		var layout = new DynamicLayout
		{
			DefaultPadding = 10,
			DefaultSpacing = new Size(10, 10),
		};

		layout.BeginVertical(yscale: true);
			
		layout.BeginGroup("Now Playing");
		PlayingLabel = new();
		var copyButton = new Button {Text = "Copy Name"};
		var copyCommand = new Command();
		copyCommand.Executed += (sender, args) => Clipboard.Instance.Text = DataManager.GetPlaying() + " ds rom";
		copyButton.Command = copyCommand;
		layout.AddRow(PlayingLabel, null, copyButton);
		layout.EndGroup();
			
		layout.BeginGroup("Status");
		StatusDropDown = new(){SelectedValue = Status.Complete};
		StatusText = new(){Enabled = false, ReadOnly = true};
		StatusDropDown.SelectedValueChanged += OnStatusChanged;
		layout.AddRow(null, StatusDropDown, StatusText);
		layout.EndGroup();
			
		layout.BeginGroup("Rating");
		var oneStar = new RadioButton{Text = "1"};
		oneStar.Checked = true;
		StarButtons = new() {oneStar};
		layout.BeginHorizontal();
		layout.Add(null);
		layout.Add(oneStar);
		for (var i = 2; i <= 5; i++)
		{
			var r = new RadioButton(oneStar){Text = $"{i}"};
			StarButtons.Add(r);
			layout.Add(r);
		}
		layout.EndGroup();

		layout.BeginGroup("Screenshots", yscale: true);
		var grid = new GridView();
		grid.Columns.Add(new GridColumn {HeaderText = "Image Path", DataCell = new TextBoxCell("ImagePath"), Editable = true, Width = 250});
		grid.Columns.Add(new GridColumn {HeaderText = "Title", DataCell = new TextBoxCell("Title"), Editable = true, Width = 250});
		Screenshots = new();
		grid.DataStore = Screenshots;

		grid.AllowDrop = true;
		grid.DragEnter += (s, e) => e.Effects = DragEffects.Link;
		grid.DragDrop += OnScreenshotDropped;
		layout.AddRow(grid);
		layout.EndGroup();

		layout.BeginGroup("Notes", yscale: true);
		NotesText = new();
		layout.AddRow(NotesText);
		layout.EndGroup();
		layout.EndVertical();

		layout.BeginVertical(yscale: false);
		var submitCommand = new Command();
		submitCommand.Executed += DoSubmit;
		SubmitButton = new Button {Text = "Submit", Command = submitCommand};
		layout.AddRow(null, SubmitButton);
		layout.EndVertical();
			
		Content = layout;
			
		var quitCommand = new Command { MenuText = "Quit", Shortcut = Application.Instance.CommonModifier | Keys.Q };
		quitCommand.Executed += (sender, e) => Application.Instance.Quit();

		var aboutCommand = new Command { MenuText = "About..." };
		aboutCommand.Executed += (sender, e) => new AboutDialog().ShowDialog(this);

		var regenerateCommand = new Command {MenuText = "Regenerate Website"};
		regenerateCommand.Executed += (sender, e) => WebsiteManager.GenerateWebsite();

		Menu = new MenuBar
		{
			QuitItem = quitCommand,
			AboutItem = aboutCommand,
			Items =
			{
				new ButtonMenuItem
				{
					Text = "&Tools",
					Items =
					{
						regenerateCommand,
					}
				}
			}
		};

		ResetState();
	}

	private void OnScreenshotDropped(object? sender, DragEventArgs e)
	{
		if (!e.Data.ContainsUris)
		{
			return;
		}

		foreach (var u in e.Data.Uris)
		{
			var s = new ScreenshotItem();
			s.ImagePath = u.LocalPath;
			switch (Screenshots.Count)
			{
				case 0:
					s.Title = "title";
					break;
				case 1:
					s.Title = "gameplay";
					break;
				case 2:
					s.Title = "credits";
					break;
				default:
					break;
			}
			Screenshots.Add(s);
		}
	}

	private void OnStatusChanged(object? sender, EventArgs e)
	{
		var isOther = StatusDropDown.SelectedValue == Status.Other;
		StatusText.Enabled = isOther;
		StatusText.ReadOnly = !isOther;
	}

	private void ResetState()
	{
		var nowPlaying = DataManager.GetPlaying();
		PlayingLabel.Text = nowPlaying ?? "Nothing? Complete?";
		StatusDropDown.SelectedValue = Status.Complete;
		StatusText.Text = "";
		StatusText.Enabled = false;
		StatusText.ReadOnly = true;
		StarButtons[2].Checked = true;
		Screenshots.Clear();
		NotesText.Text = "";
		SubmitButton.Enabled = nowPlaying != null;
	}

	private void DoSubmit(object? sender, EventArgs e)
	{
		// TODO: Update data, rebuild website
		var rating = StarButtons.FindIndex(r => r.Checked) + 1;
			
		var next = DataManager.CycleNextGame();
		var shortname = DataManager.WriteCompletedGame(StatusDropDown.SelectedValue, StatusText.Text, rating, NotesText.Text);
			
		ScreenshotManager.CopyScreenshots(Screenshots, shortname);
			
		WebsiteManager.GenerateWebsite();

		MessageBox.Show(this, $"Next up is {next}");

			
		ResetState();
	}
}
