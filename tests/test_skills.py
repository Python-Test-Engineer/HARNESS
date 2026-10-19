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
            (root / "alpha.md").write_text(
                "---\nname: alpha\ndescription: Format status messages.\n---\nSay status clearly.\n",
                encoding="utf-8",
            )

            self.assertEqual(
                discover_skills(root),
                [
                    {"name": "alpha", "description": "Format status messages."},
                    {"name": "zebra", "description": "A later skill."},
                ],
            )

    def test_read_skill_returns_body_for_a_known_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "brief.md").write_text(
                "---\nname: brief\ndescription: Keep responses concise.\n---\n\nUse brief sentences.\n",
                encoding="utf-8",
            )

            self.assertEqual(read_skill("brief", root), "Use brief sentences.")

    def test_read_skill_rejects_unknown_names(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "Unknown skill"):
                read_skill("../secret", Path(directory))

    def test_catalog_prompt_lists_discovered_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "brief.md").write_text(
                "---\nname: brief\ndescription: Keep responses concise.\n---\nInstructions.\n",
                encoding="utf-8",
            )

            self.assertEqual(
                skill_catalog_prompt(root), "- brief: Keep responses concise."
            )

    def test_agent_prompt_exposes_skill_catalog_and_selection_rule(self):
        self.assertIn(
            "txt-output: Prefix generated files.",
            agent.SYSTEM_PROMPT,
        )
        self.assertIn("load_skill", agent.SYSTEM_PROMPT)

    def test_agent_loads_txt_output_skill_when_selected(self):
        skill_call = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "tool_calls": [{
                        "id": "call-1",
                        "function": {
                            "name": "load_skill",
                            "arguments": '{"name":"txt-output"}',
                        },
                    }],
                }
            }]
        }
        final_reply = {
            "choices": [{"message": {"role": "assistant", "content": "The file has the required prefix."}}]
        }
        sent_messages = []

        def mock_chat(messages):
            sent_messages.append([dict(message) for message in messages])
            return [skill_call, final_reply][len(sent_messages) - 1]

        output = StringIO()
        console = Console(file=output, force_terminal=True, color_system="standard")

        with patch.object(agent, "chat", side_effect=mock_chat), patch.object(
            agent, "console", console
        ):
            agent.agent_loop("Create a prefixed text file")

        self.assertIn("txt-output: Prefix generated files.", sent_messages[0][0]["content"])
        self.assertIn("This is Craig West's minimal coding agent", sent_messages[1][-1]["content"])
        self.assertIn("The file has the required prefix.", output.getvalue())

    def test_discovery_rejects_invalid_frontmatter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.md").write_text("No YAML frontmatter", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "bad.md"):
                discover_skills(root)


if __name__ == "__main__":
    unittest.main()
