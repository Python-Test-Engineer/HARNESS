import json
import os
import unittest
from unittest.mock import patch

import agent_utils


class UtilityTests(unittest.TestCase):
    def test_model_uses_process_environment_value(self):
        with patch.dict(os.environ, {"MODEL": "test/model"}):
            self.assertEqual(agent_utils._model(), "test/model")

    def test_chat_sends_the_tool_schemas(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b'{"choices": []}'

        with patch.dict(
            os.environ,
            {"MODEL": "test/model", "OPENROUTER_API_KEY": "test-key"},
        ), patch("agent_utils.urllib.request.urlopen", return_value=Response()) as urlopen:
            self.assertEqual(agent_utils.chat([{"role": "user", "content": "hi"}]), {"choices": []})

        request = urlopen.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(body["model"], "test/model")
        self.assertEqual(body["tools"], agent_utils.TOOL_SCHEMAS)
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")


if __name__ == "__main__":
    unittest.main()
