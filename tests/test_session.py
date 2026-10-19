import unittest
from io import StringIO
from unittest.mock import patch

import agent
from rich.console import Console


class SessionTests(unittest.TestCase):
    def test_follow_up_turn_receives_previous_user_and_assistant_messages(self):
        replies = [
            {"choices": [{"message": {"role": "assistant", "content": "Created the initial file."}}]},
            {"choices": [{"message": {"role": "assistant", "content": "Added the requested change."}}]},
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True, color_system="standard")

        with patch.object(agent, "chat", side_effect=replies) as chat, patch.object(
            agent, "console", console
        ):
            history = agent.agent_loop("Create a starter file")
            history = agent.agent_loop("Now add a test", messages=history)

        second_turn_messages = chat.call_args_list[1].args[0]
        self.assertEqual(second_turn_messages[1], {"role": "user", "content": "Create a starter file"})
        self.assertEqual(second_turn_messages[2]["role"], "assistant")
        self.assertEqual(second_turn_messages[2]["content"], "Created the initial file.")
        self.assertEqual(second_turn_messages[3], {"role": "user", "content": "Now add a test"})
        self.assertEqual(history[-1]["content"], "Added the requested change.")

    def test_run_session_keeps_asking_until_blank_and_reuses_history(self):
        follow_ups = iter(["Add a test", ""])
        history = [{"role": "system", "content": "system prompt"}]

        with patch.object(agent, "agent_loop", return_value=history) as agent_loop:
            agent.run_session(
                "Create a starter file",
                input_fn=lambda prompt: next(follow_ups),
            )

        self.assertEqual(agent_loop.call_count, 2)
        self.assertEqual(agent_loop.call_args_list[0].args[0], "Create a starter file")
        self.assertEqual(agent_loop.call_args_list[1].args[0], "Add a test")
        self.assertIs(agent_loop.call_args_list[1].kwargs["messages"], history)

    def test_follow_up_retains_tool_calls_and_tool_results(self):
        replies = [
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": "call-1",
                                    "function": {
                                        "name": "write_file",
                                        "arguments": '{"path":"app.py","content":"print(1)"}',
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
            {"choices": [{"message": {"role": "assistant", "content": "Created app.py."}}]},
            {"choices": [{"message": {"role": "assistant", "content": "Updated app.py."}}]},
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True, color_system="standard")

        with patch.object(agent, "chat", side_effect=replies) as chat, patch.object(
            agent, "TOOLS", {"write_file": lambda **kwargs: "Created app.py"}
        ), patch.object(agent, "console", console):
            history = agent.agent_loop("Create app.py", max_steps=2)
            agent.agent_loop("Now update it", messages=history)

        follow_up_messages = chat.call_args_list[2].args[0]
        self.assertTrue(any(message.get("tool_calls") for message in follow_up_messages))
        self.assertTrue(
            any(message.get("role") == "tool" and message.get("content") == "Created app.py"
                for message in follow_up_messages)
        )
        self.assertTrue(
            any(message.get("content") == "Created app.py." for message in follow_up_messages)
        )


if __name__ == "__main__":
    unittest.main()
