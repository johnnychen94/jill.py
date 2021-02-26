from jill.utils.version_utils import latest_version
from jill.utils.version_utils import is_version_released

import unittest


class TestVersions(unittest.TestCase):
    def test_is_version_released(self):
        self.assertTrue(is_version_released("1.1.0", "windows", "x86_64"))
        self.assertFalse(is_version_released("1.1.0", "whatever", "x86_64"))

        self.assertTrue(is_version_released("1.1.1", "macos", "x86_64"))
        self.assertTrue(is_version_released("1.6.0", "windows", "x86_64"))
        self.assertTrue(is_version_released("1.6.0", "linux", "x86_64"))
        
        self.assertFalse(is_version_released("1.5.10", "windows", "x86_64"))

        self.assertTrue(is_version_released("0.1.2", "macos", "x86_64"))
        self.assertFalse(is_version_released("0.1.2", "windows", "x86_64"))
        self.assertFalse(is_version_released("0.1.2", "macos", "i686"))

        self.assertTrue(is_version_released("latest", "macos", "x86_64"))

        self.assertTrue(is_version_released("1.6.0-rc1", "macos", "x86_64", stable_only=False))
        self.assertFalse(is_version_released("1.6.0-rc1", "macos", "x86_64", stable_only=True))

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
            latest_version("1.5", "macos", "x86_64"),
            "1.5.4")
        self.assertEqual(
            latest_version("1.8", "macos", "x86_64"),
            "1.6.0")
        self.assertNotEqual(
            latest_version("", "macos", "x86_64"),
            "latest")
        self.assertEqual(
            latest_version("", "illegal_system", "x86_64"),
            latest_version("", "linux", "x86_64"))
        self.assertEqual(
            latest_version("1.4.0-rc1", "windows", "x86_64"),
            "1.4.0-rc1")
        self.assertEqual(
            latest_version("999.999.999", "windows", "x86_64"),
            "999.999.999")
        self.assertEqual(
            latest_version("1.6", "linux", "ARMv7"),
            "1.4.1")
