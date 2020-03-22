from jill.utils.version_utils import latest_version
from jill.utils.version_utils import latest_major_version
from jill.utils.version_utils import latest_minor_version
from jill.utils.version_utils import latest_patch_version

import unittest


class TestVersions(unittest.TestCase):
    def test_latest_version(self):
        self.assertEqual(
            latest_version("latest", "windows", "x86_64"),
            "latest")
        self.assertEqual(
            latest_version("0.7", "windows", "x86_64"),
            "0.7.0")
        self.assertEqual(
            latest_version("1.1", "windows", "x86_64"),
            "1.1.1")
        self.assertEqual(
            latest_version("1.4.0-rc1", "windows", "x86_64"),
            "1.4.0-rc1")
        self.assertEqual(
            latest_version("999.999.999", "windows", "x86_64"),
            "999.999.999")

    def test_latest_major_version(self):
        self.assertEqual(
            latest_major_version("latest", "windows", "x86_64"),
            "latest")
        self.assertEqual(
            latest_major_version("1.4.0-rc1", "windows", "x86_64"),
            "1.4.0-rc1")
        self.assertEqual(
            latest_major_version("999.999.999", "windows", "x86_64"),
            "999.999.999")

    def test_latest_minor_version(self):
        self.assertEqual(
            latest_minor_version("latest", "windows", "x86_64"),
            "latest")
        self.assertEqual(
            latest_minor_version("1.4.0-rc1", "windows", "x86_64"),
            "1.4.0-rc1")
        self.assertEqual(
            latest_minor_version("999.999.999", "windows", "x86_64"),
            "999.999.999")

    def test_latest_patch_version(self):
        self.assertEqual(
            latest_patch_version("latest", "windows", "x86_64"),
            "latest")
        self.assertEqual(
            latest_patch_version("1.1", "windows", "x86_64"),
            "1.1.1")
        self.assertEqual(
            latest_patch_version("1.1.0", "windows", "x86_64"),
            "1.1.1")
        self.assertEqual(
            latest_patch_version("1.4.0-rc1", "windows", "x86_64"),
            "1.4.0-rc1")
        self.assertEqual(
            latest_patch_version("999.999.999", "windows", "x86_64"),
            "999.999.999")
