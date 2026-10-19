import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import agent
import agent_commands
from agent_commands import format_size_report, load_command
from rich.console import Console


class CommandIntegrationTests(unittest.TestCase):
    def test_show_prompt_prints_the_assembled_prompt_without_calling_model(self):
        output = StringIO()
        console = Console(file=output, force_terminal=True, color_system="standard")

        with patch.object(agent, "console", console), patch.object(agent, "chat") as chat:
            agent.agent_loop("/SHOW_PROMPT")

        self.assertIn(agent.SYSTEM_PROMPT, output.getvalue())
        self.assertIn("Command /SHOW_PROMPT instructions:", output.getvalue())
        command = agent_commands.load_command("/SHOW_PROMPT")
        assert command is not None
        system_prompt = (
            agent.SYSTEM_PROMPT
            + "\n\nCommand /SHOW_PROMPT instructions:\n"
            + command[1]
        )
        self.assertIn(f"Prompt length: {len(system_prompt)} characters", output.getvalue())
        chat.assert_not_called()

    def test_agent_loads_command_file_and_displays_live_usage(self):
        with tempfile.TemporaryDirectory() as directory:
            command_path = Path(directory) / "GET_SIZE.md"
            command_path.write_text("Return measured prompt and context usage.", encoding="utf-8")
            response = {
                "choices": [{"message": {"content": "Size report complete."}}],
                "usage": {"prompt_tokens": 120, "total_tokens": 150},
            }
            sent_messages = []

            def mock_chat(messages):
                sent_messages.append([dict(message) for message in messages])
                return response

            output = StringIO()
            console = Console(file=output, force_terminal=True, color_system="standard")

            with patch.object(agent_commands, "COMMANDS_DIR", Path(directory)), patch.object(
                agent, "chat", side_effect=mock_chat
            ), patch.object(agent, "model_context_length", return_value=1000), patch.object(
                agent, "console", console
            ):
                agent.agent_loop("/GET_SIZE")

        self.assertIn("Return measured prompt and context usage.", sent_messages[0][0]["content"])
        self.assertIn("Tokens used: 150 / 1000 (15.00%)", output.getvalue())


class CommandTests(unittest.TestCase):
    def test_load_command_matches_slash_name_case_insensitively(self):
        with tempfile.TemporaryDirectory() as directory:
            command_path = Path(directory) / "GET_SIZE.md"
            command_path.write_text("Report prompt size.", encoding="utf-8")

            result = load_command("/get_size", Path(directory))

        self.assertEqual(result, ("GET_SIZE", "Report prompt size."))

    def test_load_command_only_matches_a_leading_slash_command(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "GET_SIZE.md").write_text("Instructions", encoding="utf-8")

            self.assertIsNone(load_command("Please run /GET_SIZE", Path(directory)))
            self.assertIsNone(load_command("/UNKNOWN", Path(directory)))

    def test_size_report_uses_provider_usage_and_context_window(self):
        report = format_size_report(
            "/GET_SIZE please", {"prompt_tokens": 120, "total_tokens": 150}, 1000
        )

        self.assertIn("Prompt length: 16 characters", report)
        self.assertIn("Words: 2", report)
        self.assertIn("Input tokens: 120", report)
        self.assertIn("Tokens used: 150 / 1000 (15.00%)", report)

    def test_size_report_marks_context_usage_unavailable_without_metadata(self):
        report = format_size_report("/GET_SIZE", {}, None)

        self.assertIn("Input-token usage: unavailable", report)
        self.assertIn("Context-window usage: unavailable", report)


if __name__ == "__main__":
    unittest.main()
