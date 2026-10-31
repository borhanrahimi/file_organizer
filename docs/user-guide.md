# User guide

File Organizer watches one folder (usually Downloads) and moves each new file
into a category folder in a destination you choose, with a cleaned-up name.

- [Install](#install)
- [First-time setup](#first-time-setup)
- [Everyday use](#everyday-use)
- [What happens to your files](#what-happens-to-your-files)
- [Troubleshooting](#troubleshooting)
- [Uninstall](#uninstall)
- [Privacy](#privacy)

## Install

**Requirements:** a Mac with Apple silicon (M1 or newer). Python is not
needed; the app includes everything it uses.

1. Download `File.Organizer_<version>_aarch64.dmg` from the
   [latest release](https://github.com/borhanrahimi/file_organizer/releases/latest).
2. Open the `.dmg` and drag **File Organizer** into **Applications**.
3. Open the app. macOS shows a message that it can't check the app for
   malicious software, because the app is not signed with a paid Apple
   developer account. Click **Done**.
4. Open **System Settings → Privacy & Security**, scroll down, and click
   **Open Anyway** next to the message about File Organizer. Confirm with
   your password or Touch ID.

You only need to approve it once. On an Intel Mac, Windows, or Linux, see
the [development guide](development.md) to run it from source.

## First-time setup

1. **Choose the source folder,** the folder to keep tidy, such as Downloads.
2. **Choose the destination folder,** where sorted files go, such as a new
   `Organized` folder. It must not be the source folder itself, or a folder
   that contains the source folder.
3. Click **Save folders**.
4. Review the categories on screen.
5. Click **Start**.

When you click Start, the app also sorts files that are **already** in the
source folder, including files inside its subfolders. If you only want to try
it out first, use an empty test folder as the source.

macOS may ask whether File Organizer can access a folder such as Downloads or
Documents. Click **Allow**, otherwise files there can't be moved.

## Everyday use

| You want to | Do this |
|---|---|
| See whether it's running | Look at the badge at the top right: **Running**, **Stopped**, or **Needs attention** |
| Pause sorting | Click **Stop**. A move that has already started finishes first. |
| See what happened | Check **Recent activity**: the last 100 moves and errors, newest first |
| Find your sorted files | Click **Show destination** |
| Change folders | Click **Stop**, choose new folders, click **Save folders**, then **Start** |

**Closing the window stops the organizer.** Keep the window open (it can be
minimized) for files to keep being sorted. The app does not start
automatically when you log in.

## What happens to your files

**Categories.** Files are sorted by extension:

| Folder | Extensions |
|---|---|
| Images | `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.webp` |
| Documents | `.pdf` `.docx` `.txt` `.xlsx` |
| Videos | `.mp4` `.avi` `.mov` |
| Music | `.mp3` `.wav` `.flac` |
| Archives | `.zip` `.rar` `.tar.gz` |
| Others | everything else |

Capitalization doesn't matter: `.JPG` counts as `.jpg`.

**Names.** Each word is capitalized, spaces become underscores, and
parentheses are removed. The extension is kept as it was.

| Before | After |
|---|---|
| `final_report FINAL (2).docx` | `Final_Report_Final_2.docx` |
| `IMG 2041.PNG` | `Img_2041.PNG` |
| `my-file_v2 (copy).txt` | `My-File_V2_Copy.txt` |

Capitalization is simple and occasionally odd, for example `Don'T_Panic.pdf`
or `At_11.42.53_Pm` in screenshot names.

**Nothing is overwritten.** If the destination already has a file with that
name, the new one gets a number: `Invoice_1.pdf`, `Invoice_2.pdf`, and so on.

**Unfinished downloads are left alone.** Files ending in `.crdownload`,
`.part`, or `.download` are skipped until the browser renames them. Every
file must also stay unchanged for three seconds before it is moved.

**Skipped files.** `.DS_Store` files and files already inside the destination
folder are never moved.

**Moves can't be undone from the app.** Recent activity shows where each
file went, so you can move it back by hand.

## Troubleshooting

**"Another file organizer is already running."**
Only one organizer can run at a time. Quit any other copy of File Organizer.
If you also run it from the terminal or as a LaunchAgent, stop that first.

**"watch_folder must not be the same as, or inside, destination_root."**
The source can't be the destination itself or a folder inside it. Choose a
destination that doesn't contain the source, for example a new `Organized`
folder next to Downloads.

**"watch_folder is not an existing folder."**
The source folder was moved, renamed, or deleted. Choose it again.

**A file wasn't moved.**
- Wait a few seconds; files are moved once they stop changing.
- Check that it isn't still downloading (`.crdownload`, `.part`, `.download`).
- Check **Recent activity** for an error. Errors are retried automatically.
- If the error says **Operation not permitted**, open **System Settings →
  Privacy & Security → Files and Folders** and allow File Organizer to use
  that folder.

**The window says "Waiting for the organizer backend to start…"**
The first launch takes a few seconds. If the message doesn't go away, quit
and reopen the app.

**The status says "Needs attention."**
Read the message under **Status**. Usually the source folder was removed
while the organizer was running. Fix the folder, then click **Start** again.

**Something else.** Please
[open an issue](https://github.com/borhanrahimi/file_organizer/issues/new/choose)
and include the message you see and your macOS version.

## Uninstall

1. Quit File Organizer.
2. Drag **File Organizer** from **Applications** to the Trash.
3. Optionally delete its settings. In Finder, choose **Go → Go to Folder**
   and remove these two folders:
   - `~/Library/Application Support/com.borhan.file-organizer`
   - `~/Library/Application Support/File Organizer`

Your sorted files are not affected.

## Privacy

File Organizer works entirely on your computer. It does not upload files,
collect usage data, or connect to the internet. The app and its background
process talk to each other only on your own computer (`127.0.0.1`), using a
secret that changes every time the app starts.
