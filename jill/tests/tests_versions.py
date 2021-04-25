from jill.utils.version_utils import latest_version
from jill.utils.version_utils import is_version_released

import unittest


class TestVersions(unittest.TestCase):
    def test_is_version_released(self):
        self.assertTrue(is_version_released("1.1.0", "winnt", "x86_64"))
        self.assertFalse(is_version_released("1.1.0", "whatever", "x86_64"))

        self.assertTrue(is_version_released("1.1.1", "mac", "x86_64"))
        self.assertTrue(is_version_released("1.6.0", "winnt", "x86_64"))
        self.assertTrue(is_version_released("1.6.0", "linux", "x86_64"))

        self.assertFalse(is_version_released("1.5.10", "winnt", "x86_64"))

        self.assertTrue(is_version_released("latest", "mac", "x86_64"))

        self.assertTrue(is_version_released(
            "1.6.0-rc1", "mac", "x86_64", stable_only=False))
        self.assertFalse(is_version_released(
            "1.6.0-rc1", "mac", "x86_64", stable_only=True))

    def test_latest_version(self):
        self.assertEqual(
            latest_version("latest", "winnt", "x86_64"),
            "latest")
        self.assertEqual(
            latest_version("0.7", "winnt", "x86_64"),
            "0.7.0")
        self.assertEqual(
            latest_version("1.1", "winnt", "x86_64"),
            "1.1.1")
        self.assertEqual(
            latest_version("1.5", "mac", "x86_64"),
            "1.5.4")
        self.assertNotEqual(
            latest_version("", "mac", "x86_64"),
            "latest")
        self.assertRaises(ValueError, latest_version,
                          "", "illegal_system", "x86_64")
        self.assertEqual(
            latest_version("1.4.0-rc1", "winnt", "x86_64"),
            "1.4.0-rc1")
        self.assertEqual(
            latest_version("999.999.999", "winnt", "x86_64"),
            "999.999.999")
        self.assertEqual(
            latest_version("999.999", "linux", "armv7l"),
            latest_version("", "linux", "armv7l"))
