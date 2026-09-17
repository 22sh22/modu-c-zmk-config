#!/usr/bin/env python3
"""Regression checks for Studio integration mistakes that can still compile."""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import validate


class StudioValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "config-repo"
        shutil.copytree(validate.ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        replacement = patch.object(validate, "ROOT", self.root)
        replacement.start()
        self.addCleanup(replacement.stop)

    def replace(self, path, old, new):
        target = self.root / path
        text = target.read_text(encoding="utf-8")
        self.assertIn(old, text)
        target.write_text(text.replace(old, new, 1), encoding="utf-8")

    def test_studio_configuration_passes(self):
        validate.check_metadata()
        validate.check_physical_layout()
        validate.check_keymap()
        validate.check_build_files()

    def test_missing_studio_flag_rejected(self):
        self.replace("build.yaml", "      -DCONFIG_ZMK_STUDIO=y\n", "")
        with self.assertRaisesRegex(SystemExit, "enable Studio only on the central"):
            validate.check_build_files()

    def test_peripheral_usb_rpc_rejected(self):
        self.replace("build.yaml", "    shield: modu_right\n",
                     "    shield: modu_right\n    snippet: studio-rpc-usb-uart\n")
        with self.assertRaisesRegex(SystemExit, "only for modu_left"):
            validate.check_build_files()

    def test_unquoted_cmake_module_list_rejected(self):
        self.replace("build.yaml", '      "-DZMK_EXTRA_MODULES=', '      -DZMK_EXTRA_MODULES=')
        self.replace("build.yaml", '/zmk-pmw3610-driver"', '/zmk-pmw3610-driver')
        # shlex alone drops quoting, so the semicolon remains one token even
        # though the shell would interpret it as a command separator.
        with self.assertRaises(SystemExit):
            validate.check_build_files()

    def test_reordered_physical_positions_rejected(self):
        self.replace("config/modu-layouts.dtsi",
                     "100 100    0    0", "100 100  100    0")
        with self.assertRaisesRegex(SystemExit, "67 JSON positions"):
            validate.check_physical_layout()

    def test_thumb_remap_bypass_rejected(self):
        self.replace("config/modu-layouts.dtsi", "kscan = <&alt_thumb_kscan>;", "kscan = <&kscan0>;")
        with self.assertRaisesRegex(SystemExit, "alt_thumb_kscan"):
            validate.check_physical_layout()

    def test_unlock_key_removal_rejected(self):
        self.replace("config/modu.keymap", "&studio_unlock", "&trans")
        with self.assertRaisesRegex(SystemExit, r"Fn\+R"):
            validate.check_keymap()


if __name__ == "__main__":
    unittest.main()
