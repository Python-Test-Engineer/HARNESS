# Mini Coding Agent Harness

A small, educational coding-agent demo. Give it a natural-language task and it uses an OpenRouter chat model in a ReAct loop: the model requests a tool, the agent runs it, returns the result to the model, and repeats until it produces a final response or reaches the step limit.

## Available tools

- `write_file`, `edit_file`, and `read_file` for working with files.
- `list_files` to list entries in `work/` or one of its subdirectories.
- `run` for executing shell commands with `work/` as the working directory.

The loop and tool dispatcher are implemented in `agent.py`; `rich` formats the console output.

## Run

Install dependencies with `uv sync`, then start the agent with a request:

```sh
uv run agent.py "write a hello world script and run it"
```

If no request is passed on the command line, the program prompts for one. Files created by the demo go in `work/`.

## Configuration

Set `OPENROUTER_API_KEY` in the process environment or in the project-root `.env` file. Optionally set `MODEL` there to choose the OpenRouter model. For both settings, an existing process environment value takes precedence over the `.env` value. The `.env` file is ignored by Git; keep credentials out of source control.

## Limitations

This is a minimal teaching harness, not a production agent or security sandbox. The model can request shell commands, which run with the permissions of the user running the program. Review the code and requests before using it with sensitive data or on an untrusted task.
