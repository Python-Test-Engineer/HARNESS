from io import StringIO
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import agent
from rich.console import Console

from agent_skills import discover_skills, read_skill, skill_catalog_prompt


class SkillLoadingTests(unittest.TestCase):
    def test_discovery_reads_yaml_frontmatter_and_sorts_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "zebra.md").write_text(
                "---\nname: zebra\ndescription: A later skill.\n---\nDo zebra things.\n",
                encoding="utf-8",
            )
            (root / "hello.md").write_text(
                "---\nname: hello\ndescription: Format HELLO greetings.\n---\nSay HELLO in color.\n",
                encoding="utf-8",
            )

            self.assertEqual(
                discover_skills(root),
                [
                    {"name": "hello", "description": "Format HELLO greetings."},
                    {"name": "zebra", "description": "A later skill."},
                ],
            )

    def test_read_skill_returns_body_for_a_known_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "hello.md").write_text(
                "---\nname: hello\ndescription: Format HELLO greetings.\n---\n\nSay HELLO in color.\n",
                encoding="utf-8",
            )

            self.assertEqual(read_skill("hello", root), "Say HELLO in color.")

    def test_read_skill_rejects_unknown_names(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "Unknown skill"):
                read_skill("../secret", Path(directory))

    def test_catalog_prompt_lists_discovered_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "hello.md").write_text(
                "---\nname: hello\ndescription: Format HELLO greetings.\n---\nInstructions.\n",
                encoding="utf-8",
            )

            self.assertEqual(
                skill_catalog_prompt(root), "- hello: Format HELLO greetings."
            )

    def test_agent_prompt_exposes_skill_catalog_and_selection_rule(self):
        self.assertIn(
            "hello: Prefix generated files and format HELLO greetings as colored ASCII art.",
            agent.SYSTEM_PROMPT,
        )
        self.assertIn("load_skill", agent.SYSTEM_PROMPT)

    def test_agent_loads_relevant_skill_before_rendering_its_greeting(self):
        hello_skill = agent.TOOLS["load_skill"]("hello")
        ascii_art = hello_skill.split("[bold bright_cyan]\n", 1)[1].split(
            "\n[/bold bright_cyan]", 1
        )[0]
        skill_call = {
            "choices": [
                {
                    "message": {
                        "tool_calls": [
                            {
                                "id": "call-1",
                                "function": {
                                    "name": "load_skill",
                                    "arguments": '{"name":"hello"}',
                                },
                            }
                        ]
                    }
                }
            ]
        }
        final_reply = {
            "choices": [
                {
                    "message": {
                        "content": f"[bold bright_cyan]\n{ascii_art}\n[/bold bright_cyan]"
                    }
                }
            ]
        }
        output = StringIO()
        console = Console(file=output, force_terminal=True, color_system="standard")

        with patch.object(agent, "chat", side_effect=[skill_call, final_reply]) as chat, patch.object(
            agent, "console", console
        ):
            agent.agent_loop("hello")

        messages = chat.call_args_list[1].args[0]
        self.assertIn("hello: Prefix generated files and format HELLO greetings as colored ASCII art.", messages[0]["content"])
        self.assertIn("Whenever the assistant gives a HELLO greeting", messages[-1]["content"])
        self.assertIn("\x1b[", output.getvalue())
        self.assertIn("_____", output.getvalue())

    def test_discovery_rejects_invalid_frontmatter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.md").write_text("No YAML frontmatter", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "bad.md"):
                discover_skills(root)


if __name__ == "__main__":
    unittest.main()
