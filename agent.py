"""Mini coding agent — a tiny functional harness for the AI-agents talk.

A real ReAct loop: type a request, and the agent uses its tools
(write/edit/read files, run commands) until it has an answer.

    think -> tool call -> result -> repeat -> final answer

LLM settings are read from environment variables first, then from this
project's .env file (OPENROUTER_API_KEY and optionally MODEL).

Run:  uv run agent.py "write a hello world script and run it"
"""

from __future__ import annotations

import json
import sys

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from agent_commands import format_size_report, load_command
from agent_skills import skill_catalog_prompt
from agent_tools import TOOLS
from agent_utils import chat, model_context_length

console = Console()

SYSTEM_PROMPT = (
    "You are a minimal coding agent. You can write, edit and read files "
    "in the work directory, list its files, and run shell commands there. Work step by step: "
    "create the script, run it, fix any errors, and confirm the final output. "
    "Before acting or replying, check the available skills below. If a skill directly "
    "applies, call load_skill with its name and follow its instructions; do not load "
    "unrelated skills. Finish with a short plain-text summary of what you did."
    "\n\nAvailable skills:\n"
    + skill_catalog_prompt()
)


# --------------------------------------------------------------------------
# THE LOOP
# --------------------------------------------------------------------------
def agent_loop(
    prompt: str,
    max_steps: int = 8,
    messages: list[dict] | None = None,
) -> list[dict]:
    command = load_command(prompt)
    console.rule("[bold cyan]mini coding agent[/bold cyan]", style="cyan")
    console.print(
        Panel(
            prompt, title="[bold]request[/bold]", border_style="yellow", padding=(0, 1)
        )
    )
    console.print()

    if messages is None:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    base_system_prompt = messages[0]["content"]
    if command:
        command_name, instructions = command
        system_prompt = (
            f"{base_system_prompt}\n\nCommand /{command_name} instructions:\n{instructions}"
        )
        if command_name.casefold() == "show_prompt":
            console.print("[bold]Current system prompt:[/bold]")
            console.print(system_prompt, markup=False, highlight=False, soft_wrap=True)
            console.print(
                f"\nPrompt length: {len(system_prompt)} characters",
                markup=False,
                highlight=False,
            )
            return messages
        messages[0]["content"] = system_prompt
    messages.append({"role": "user", "content": prompt})

    latest_usage = {}
    for step in range(1, max_steps + 1):
        reply = chat(messages)
        if isinstance(reply.get("usage"), dict):
            latest_usage = reply["usage"]
        msg = reply["choices"][0]["message"]

        if msg.get("content"):
            console.print(
                Panel(
                    msg["content"],
                    title=f"[bold]Step {step} — thought[/bold]",
                    border_style="magenta",
                    padding=(0, 1),
                )
            )

        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            messages.append(msg)
            console.print()
            console.rule("[bold cyan]done[/bold cyan]", style="cyan")
            if command:
                _print_size_report(prompt, latest_usage)
            messages[0]["content"] = base_system_prompt
            return messages

        messages.append(msg)
        for tc in tool_calls:
            name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"] or "{}")
            except json.JSONDecodeError:
                args = {}
            console.print(f"[bold green]tool[/bold green] {name}({json.dumps(args)})")
            if name == "write_file":
                console.print(
                    Syntax(args.get("content", ""), "python", theme="monokai")
                )
            try:
                result = TOOLS[name](**args)
            except Exception as e:  # surface tool errors back to the model
                result = f"ERROR: {e}"
            console.print(
                Panel(
                    result,
                    title="[bold]result[/bold]",
                    border_style="green",
                    padding=(0, 1),
                )
            )
            messages.append(
                {"role": "tool", "tool_call_id": tc["id"], "content": result}
            )
        console.print()

    console.print("[bold red]max steps reached[/bold red]")
    if command:
        _print_size_report(prompt, latest_usage)
    messages[0]["content"] = base_system_prompt
    return messages


def _print_size_report(prompt: str, usage: dict) -> None:
    report = format_size_report(prompt, usage, model_context_length())
    console.print(
        Panel(
            report,
            title="[bold]GET_SIZE[/bold]",
            border_style="cyan",
            padding=(0, 1),
        )
    )


def run_session(
    initial_prompt: str | None = None,
    max_steps: int = 8,
    input_fn=input,
) -> None:
    """Run consecutive prompts in one conversation until blank input or exit."""
    messages = None
    prompt = initial_prompt
    while True:
        if prompt is None:
            try:
                prompt = input_fn("Request: ")
            except EOFError:
                return
        prompt = prompt.strip()
        if not prompt or prompt.casefold() in {"/exit", "/quit"}:
            return

        messages = agent_loop(prompt, max_steps=max_steps, messages=messages)
        try:
            prompt = input_fn("Follow-up request (blank or /exit to finish): ")
        except EOFError:
            return


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]).strip()
    run_session(prompt or None)
