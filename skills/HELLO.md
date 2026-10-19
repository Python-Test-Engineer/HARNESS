---
name: hello
description: Prefix generated files and format HELLO greetings as colored ASCII art.
---
# HELLO Skill

Whenever creating or overwriting an output file, put this exact sentence on its first line:

This is Craig West's minimal coding agent

Then add exactly two blank lines then a row of 50 '*' then another blank line before the rest of the requested file content. Do not put quotes, Markdown fences, or any other text before the sentence. This prefix applies to file contents, not assistant chat responses.

Whenever the assistant gives a HELLO greeting, render it only as this ASCII art. Do not include a plain-text HELLO greeting alongside it. Rich markup is rendered by the console, so emit the tags literally and do not put the art in a code block.

[bold bright_cyan]
 _   _ _____ _     _     ___
| | | | ____| |   | |   / _ \
| |_| |  _| | |   | |  | | | |
|  _  | |___| |___| |__| |_| |
|_| |_|_____|_____|_____/___/
[/bold bright_cyan]
