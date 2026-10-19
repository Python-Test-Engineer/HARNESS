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

from agent_tools import TOOLS
from agent_utils import chat

console = Console()

SYSTEM_PROMPT = (
    "You are a minimal coding agent. You can write, edit and read files "
    "in the work directory, list its files, and run shell commands there. Work step by step: "
    "create the script, run it, fix any errors, and confirm the final output. "
    "Finish with a short plain-text summary of what you did."
)


# --------------------------------------------------------------------------
# THE LOOP
# --------------------------------------------------------------------------
def agent_loop(prompt: str, max_steps: int = 8) -> None:
    console.rule("[bold cyan]mini coding agent[/bold cyan]", style="cyan")
    console.print(
        Panel(
            prompt, title="[bold]request[/bold]", border_style="yellow", padding=(0, 1)
        )
    )
    console.print()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    for step in range(1, max_steps + 1):
        reply = chat(messages)
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
            console.print()
            console.rule("[bold cyan]done[/bold cyan]", style="cyan")
            return

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


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]).strip()
    if not prompt:
        prompt = input("Request: ").strip()
    agent_loop(prompt)
