from jill.utils.filters import canonicalize_arch, canonicalize_sys

import unittest


class TestAlias(unittest.TestCase):
    def test_canonicalize_sys(self):
        self.assertEqual(canonicalize_sys("winnt"), "winnt")
        self.assertEqual(canonicalize_sys("windows"), "winnt")
        self.assertEqual(canonicalize_sys("win"), "winnt")

        self.assertEqual(canonicalize_sys("mac"), "mac")
        self.assertEqual(canonicalize_sys("macos"), "mac")
        self.assertEqual(canonicalize_sys("darwin"), "mac")

        self.assertEqual(canonicalize_sys("linux"), "linux")

        self.assertEqual(canonicalize_sys("freebsd"), "freebsd")

        # case-insensitive
        self.assertEqual(canonicalize_sys("WiNnT"), "winnt")

        # jill might just break if it maps musl to other strings...
        self.assertEqual(canonicalize_sys("musl"), "musl")

    def test_canonicalize_arch(self):
        self.assertEqual(canonicalize_arch("i686"), "i686")
        self.assertEqual(canonicalize_arch("I686"), "i686")
        self.assertEqual(canonicalize_arch("x86"), "i686")
        self.assertEqual(canonicalize_arch("X86"), "i686")

        self.assertEqual(canonicalize_arch("x64"), "x86_64")
        self.assertEqual(canonicalize_arch("X64"), "x86_64")
        self.assertEqual(canonicalize_arch("x86_64"), "x86_64")
        self.assertEqual(canonicalize_arch("X86_64"), "x86_64")

        self.assertEqual(canonicalize_arch("aarch64"), "aarch64")
        self.assertEqual(canonicalize_arch("armv8"), "aarch64")
        self.assertEqual(canonicalize_arch("ARMv8"), "aarch64")

        self.assertEqual(canonicalize_arch("armv7l"), "armv7l")
        self.assertEqual(canonicalize_arch("armv7"), "armv7l")
        self.assertEqual(canonicalize_arch("ARMv7"), "armv7l")

        # case-insensitive
        self.assertEqual(canonicalize_arch("aArCH64"), "aarch64")
