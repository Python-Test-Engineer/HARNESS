import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import agent_tools


class ToolModuleTests(unittest.TestCase):
    def test_registry_and_schemas_cover_same_tools(self):
        schema_names = {
            schema["function"]["name"] for schema in agent_tools.TOOL_SCHEMAS
        }
        self.assertEqual(schema_names, set(agent_tools.TOOLS))
        self.assertEqual(
            set(agent_tools.TOOLS),
            {"write_file", "edit_file", "read_file", "list_files", "run"},
        )

    def test_list_files_lists_sorted_entries_and_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "zeta.txt").write_text("z")
            (root / "Alpha").mkdir()
            with patch.object(agent_tools, "WORKDIR", root):
                self.assertEqual(agent_tools.list_files(), "Alpha/\nzeta.txt")

    def test_list_files_rejects_paths_outside_workspace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "work"
            root.mkdir()
            with patch.object(agent_tools, "WORKDIR", root):
                with self.assertRaises(ValueError):
                    agent_tools.list_files("../")


if __name__ == "__main__":
    unittest.main()
