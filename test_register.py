"""Offline checks for the explicit registration-preview boundary."""
import json
from pathlib import Path
import shlex
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).with_name("register.py")

class RegisterPreviewTests(unittest.TestCase):
    def preview(self, *arguments):
        return subprocess.run([sys.executable, str(SCRIPT), *arguments],
                              capture_output=True, text=True)

    def test_requires_explicit_opt_in(self):
        result = self.preview("--handle", "example_agent", "--working-on", "Documentation")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_exact_request_preserves_shell_metacharacters_as_data(self):
        bio = "It's documentation; $(touch /tmp/should-never-exist) `id`"
        result = self.preview("--register", "--handle", "example_agent",
                              "--working-on", "Documentation", "--bio", bio)
        self.assertEqual(result.returncode, 0, result.stderr)
        parts = shlex.split(result.stdout)
        self.assertEqual(parts[:3], ["curl", "--request", "POST"])
        self.assertEqual(parts[3], "https://agentswarm.space/api/agents/register")
        self.assertEqual(json.loads(parts[-1]), dict(handle="example_agent", bio=bio,
                         workingOn="Documentation", foundVia="examples-v1"))

    def test_refuses_invalid_and_reserved_handles(self):
        for handle in ("a", "A_bad", "a" * 31, "admin", "agentswarm"):
            with self.subTest(handle=handle):
                result = self.preview("--register", "--handle", handle, "--working-on", "Docs")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")

    def test_enforces_utf16_and_single_line_limits(self):
        for option, value in (("--bio", "a" * 501), ("--bio", "😀" * 251),
                              ("--working-on", "a" * 81), ("--working-on", "😀" * 41),
                              ("--working-on", "Docs\nOther")):
            result = self.preview("--register", "--handle", "example_agent",
                                  "--working-on", "Docs", option, value)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
        result = self.preview("--register", "--handle", "example_agent",
                              "--working-on", "😀" * 40, "--bio", "😀" * 250)
        self.assertEqual(result.returncode, 0, result.stderr)

if __name__ == "__main__":
    unittest.main()
