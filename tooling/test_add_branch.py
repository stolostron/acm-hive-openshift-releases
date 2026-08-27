#!/usr/bin/env python3

import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).parent / "add-branch.py"
SPEC = importlib.util.spec_from_file_location("add_branch", MODULE_PATH)
ADD_BRANCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADD_BRANCH)


class TestOcpVersionsFromAligned(unittest.TestCase):
    def test_standard_minor_window(self):
        self.assertEqual(
            ADD_BRANCH.ocp_versions_from_aligned("4.23"),
            ["4.21", "4.22", "4.23", "4.24"],
        )

    def test_5_0_rollover_window(self):
        self.assertEqual(
            ADD_BRANCH.ocp_versions_from_aligned("5.0"),
            ["4.21", "4.22", "4.23", "5.0", "5.1"],
        )

    def test_invalid_format_exits(self):
        with self.assertRaises(SystemExit):
            ADD_BRANCH.ocp_versions_from_aligned("5")


if __name__ == "__main__":
    unittest.main()
