#!/usr/bin/env python3
"""
Types a file into whatever window has focus, like a keyboard.

Usage:
	python3 type_file.py formation.py
	1. Run it, then click in the target editor within the countdown.
	2. To stop: touch /tmp/stop_typing (from another terminal).

Requires (X11): sudo apt install xdotool
Wayland: xdotool will not work in native Wayland apps; log in with "Ubuntu on Xorg".
"""
import os
import subprocess
import sys
import time

COUNTDOWN = 5          # seconds to click in the editor
CHAR_DELAY_MS = 8      # delay between characters
LINE_DELAY = 0.03      # pause after each Enter
STOP_FILE = "/tmp/stop_typing"

# True  -> after each Enter, delete the indentation the editor added
#          (PyCharm / VS Code / Sublime auto-indent), then type the real one.
# False -> for editors with no auto-indent (nano, gedit, plain text).
FIX_AUTO_INDENT = True


def xdo(*args):
	subprocess.run(["xdotool", *args], check=True)


def type_text(text):
	xdo("type", "--clearmodifiers", "--delay", str(CHAR_DELAY_MS), "--", text)


def press(key):
	xdo("key", "--clearmodifiers", key)


def main():
	if len(sys.argv) < 2:
		print("Usage: python3 type_file.py <file>")
		sys.exit(1)

	path = sys.argv[1]
	with open(path, "r", encoding="utf-8") as f:
		lines = f.read().split("\n")

	if os.path.exists(STOP_FILE):
		os.remove(STOP_FILE)

	for i in range(COUNTDOWN, 0, -1):
		print(f"Click in the editor... starting in {i}", end="\r", flush=True)
		time.sleep(1)
	print("\nTyping...                              ")

	total = len(lines)
	for n, line in enumerate(lines, 1):
		if os.path.exists(STOP_FILE):
			print("Stopped.")
			return

		if line:
			type_text(line)

		if n < total:
			press("Return")
			if FIX_AUTO_INDENT:
				# select what the editor auto-indented and remove it
				press("shift+Home")
				press("BackSpace")
			time.sleep(LINE_DELAY)

		if n % 50 == 0:
			print(f"{n}/{total} lines", end="\r", flush=True)

	print(f"Done: {total} lines typed.")


if __name__ == "__main__":
	main()