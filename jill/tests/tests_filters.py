from jill.filters import f_major_version, f_vmajor_version, f_Vmajor_version
from jill.filters import f_minor_version, f_vminor_version, f_Vminor_version
from jill.filters import f_patch_version, f_vpatch_version, f_Vpatch_version
from jill.filters import f_version
from jill.filters import f_system, f_System, f_SYSTEM
from jill.filters import f_sys, f_Sys, f_SYS
from jill.filters import f_os, f_Os, f_OS
from jill.filters import f_arch, f_Arch, f_ARCH
from jill.filters import f_osarch, f_Osarch, f_OSarch
from jill.filters import f_osbit
from jill.filters import f_bit
from jill.filters import f_extension
from jill.filters import generate_info
import unittest


class TestFilters(unittest.TestCase):

    def test_major_version(self):
        self.assertEqual(f_major_version("1.2.3"), "1")
        self.assertEqual(f_major_version("1.2.3-pre"), "1")
        self.assertEqual(f_major_version("v1.2.3"), "1")
        self.assertEqual(f_major_version("v1.2.3-pre"), "1")
        self.assertEqual(f_major_version("latest"), "latest")

        self.assertEqual(f_vmajor_version("1.2.3"), "v1")
        self.assertEqual(f_vmajor_version("1.2.3-pre"), "v1")
        self.assertEqual(f_vmajor_version("v1.2.3"), "v1")
        self.assertEqual(f_vmajor_version("v1.2.3-pre"), "v1")
        self.assertEqual(f_vmajor_version("latest"), "latest")

        self.assertEqual(f_Vmajor_version("1.2.3"), "V1")
        self.assertEqual(f_Vmajor_version("1.2.3-pre"), "V1")
        self.assertEqual(f_Vmajor_version("v1.2.3"), "V1")
        self.assertEqual(f_Vmajor_version("v1.2.3-pre"), "V1")
        self.assertEqual(f_Vmajor_version("latest"), "Latest")

    def test_minor_version(self):
        self.assertEqual(f_minor_version("1.2.3"), "1.2")
        self.assertEqual(f_minor_version("1.2.3-pre"), "1.2")
        self.assertEqual(f_minor_version("v1.2.3"), "1.2")
        self.assertEqual(f_minor_version("v1.2.3-pre"), "1.2")
        self.assertEqual(f_minor_version("latest"), "latest")

        self.assertEqual(f_vminor_version("1.2.3"), "v1.2")
        self.assertEqual(f_vminor_version("1.2.3-pre"), "v1.2")
        self.assertEqual(f_vminor_version("v1.2.3"), "v1.2")
        self.assertEqual(f_vminor_version("v1.2.3-pre"), "v1.2")
        self.assertEqual(f_vminor_version("latest"), "latest")

        self.assertEqual(f_Vminor_version("1.2.3"), "V1.2")
        self.assertEqual(f_Vminor_version("1.2.3-pre"), "V1.2")
        self.assertEqual(f_Vminor_version("v1.2.3"), "V1.2")
        self.assertEqual(f_Vminor_version("v1.2.3-pre"), "V1.2")
        self.assertEqual(f_Vminor_version("latest"), "Latest")

    def test_patch_version(self):
        self.assertEqual(f_patch_version("1.2.3"), "1.2.3")
        self.assertEqual(f_patch_version("1.2.3-pre"), "1.2.3")
        self.assertEqual(f_patch_version("v1.2.3"), "1.2.3")
        self.assertEqual(f_patch_version("v1.2.3-pre"), "1.2.3")
        self.assertEqual(f_patch_version("latest"), "latest")

        self.assertEqual(f_vpatch_version("1.2.3"), "v1.2.3")
        self.assertEqual(f_vpatch_version("1.2.3-pre"), "v1.2.3")
        self.assertEqual(f_vpatch_version("v1.2.3"), "v1.2.3")
        self.assertEqual(f_vpatch_version("v1.2.3-pre"), "v1.2.3")
        self.assertEqual(f_vpatch_version("latest"), "latest")

        self.assertEqual(f_Vpatch_version("1.2.3"), "V1.2.3")
        self.assertEqual(f_Vpatch_version("1.2.3-pre"), "V1.2.3")
        self.assertEqual(f_Vpatch_version("v1.2.3"), "V1.2.3")
        self.assertEqual(f_Vpatch_version("v1.2.3-pre"), "V1.2.3")
        self.assertEqual(f_Vpatch_version("latest"), "Latest")

    def test_version(self):
        self.assertEqual(f_version("1.2.3"), "v1.2.3")
        self.assertEqual(f_version("1.2.3-pre"), "v1.2.3-pre")
        self.assertEqual(f_version("v1.2.3"), "v1.2.3")
        self.assertEqual(f_version("v1.2.3-pre"), "v1.2.3-pre")
        self.assertEqual(f_version("latest"), "latest")

    def test_arch(self):
        self.assertEqual(f_arch("x86_64"), "x64")
        self.assertEqual(f_arch("i686"), "x86")
        self.assertEqual(f_arch("ARMv8"), "aarch64")
        self.assertEqual(f_arch("ARMv7"), "armv7l")

        self.assertEqual(f_Arch("x86_64"), "X64")
        self.assertEqual(f_Arch("i686"), "X86")
        self.assertEqual(f_Arch("ARMv8"), "Aarch64")
        self.assertEqual(f_Arch("ARMv7"), "Armv7l")

        self.assertEqual(f_ARCH("x86_64"), "X64")
        self.assertEqual(f_ARCH("i686"), "X86")
        self.assertEqual(f_ARCH("ARMv8"), "AARCH64")
        self.assertEqual(f_ARCH("ARMv7"), "ARMV7L")

    def test_system(self):
        self.assertEqual(f_system("windows"), "windows")
        self.assertEqual(f_system("linux"), "linux")
        self.assertEqual(f_system("freebsd"), "freebsd")
        self.assertEqual(f_system("macos"), "macos")

        self.assertEqual(f_System("windows"), "Windows")
        self.assertEqual(f_System("linux"), "Linux")
        self.assertEqual(f_System("freebsd"), "Freebsd")
        self.assertEqual(f_System("macos"), "Macos")

        self.assertEqual(f_SYSTEM("windows"), "WINDOWS")
        self.assertEqual(f_SYSTEM("linux"), "LINUX")
        self.assertEqual(f_SYSTEM("freebsd"), "FREEBSD")
        self.assertEqual(f_SYSTEM("macos"), "MACOS")

    def test_sys(self):
        self.assertEqual(f_sys("windows"), "winnt")
        self.assertEqual(f_sys("linux"), "linux")
        self.assertEqual(f_sys("freebsd"), "freebsd")
        self.assertEqual(f_sys("macos"), "mac")

        self.assertEqual(f_Sys("windows"), "Winnt")
        self.assertEqual(f_Sys("linux"), "Linux")
        self.assertEqual(f_Sys("freebsd"), "Freebsd")
        self.assertEqual(f_Sys("macos"), "Mac")

        self.assertEqual(f_SYS("windows"), "WINNT")
        self.assertEqual(f_SYS("linux"), "LINUX")
        self.assertEqual(f_SYS("freebsd"), "FREEBSD")
        self.assertEqual(f_SYS("macos"), "MAC")

    def test_os(self):
        self.assertEqual(f_os("windows"), "win")
        self.assertEqual(f_os("linux"), "linux")
        self.assertEqual(f_os("freebsd"), "freebsd")
        self.assertEqual(f_os("macos"), "mac")

        self.assertEqual(f_Os("windows"), "Win")
        self.assertEqual(f_Os("linux"), "Linux")
        self.assertEqual(f_Os("freebsd"), "Freebsd")
        self.assertEqual(f_Os("macos"), "Mac")

        self.assertEqual(f_OS("windows"), "WIN")
        self.assertEqual(f_OS("linux"), "LINUX")
        self.assertEqual(f_OS("freebsd"), "FREEBSD")
        self.assertEqual(f_OS("macos"), "MAC")

    def test_osarch(self):
        self.assertEqual(f_osarch("win", "i686"), "win32")
        self.assertEqual(f_osarch("win", "x86_64"), "win64")
        self.assertEqual(f_osarch("mac", "x86_64"), "mac64")
        self.assertEqual(f_osarch("linux", "ARMv7"), "linux-armv7l")
        self.assertEqual(f_osarch("linux", "ARMv8"), "linux-aarch64")
        self.assertEqual(f_osarch("linux", "i686"), "linux-i686")
        self.assertEqual(f_osarch("linux", "x86_64"), "linux-x86_64")
        self.assertEqual(f_osarch("freebsd", "x86_64"), "freebsd-x86_64")

        self.assertEqual(f_Osarch("win", "i686"), "Win32")
        self.assertEqual(f_Osarch("win", "x86_64"), "Win64")
        self.assertEqual(f_Osarch("mac", "x86_64"), "Mac64")
        self.assertEqual(f_Osarch("linux", "ARMv7"), "Linux-armv7l")
        self.assertEqual(f_Osarch("linux", "ARMv8"), "Linux-aarch64")
        self.assertEqual(f_Osarch("linux", "i686"), "Linux-i686")
        self.assertEqual(f_Osarch("linux", "x86_64"), "Linux-x86_64")
        self.assertEqual(f_Osarch("freebsd", "x86_64"), "Freebsd-x86_64")

        self.assertEqual(f_OSarch("win", "i686"), "WIN32")
        self.assertEqual(f_OSarch("win", "x86_64"), "WIN64")
        self.assertEqual(f_OSarch("mac", "x86_64"), "MAC64")
        self.assertEqual(f_OSarch("linux", "ARMv7"), "LINUX-armv7l")
        self.assertEqual(f_OSarch("linux", "ARMv8"), "LINUX-aarch64")
        self.assertEqual(f_OSarch("linux", "i686"), "LINUX-i686")
        self.assertEqual(f_OSarch("linux", "x86_64"), "LINUX-x86_64")
        self.assertEqual(f_OSarch("freebsd", "x86_64"), "FREEBSD-x86_64")

    def test_osbit(self):
        self.assertEqual(f_osbit("win", "i686"), "win32")
        self.assertEqual(f_osbit("win", "x86_64"), "win64")
        self.assertEqual(f_osbit("mac", "x86_64"), "mac64")
        self.assertEqual(f_osbit("linux", "ARMv7"), "linuxarmv7l")
        self.assertEqual(f_osbit("linux", "ARMv8"), "linuxaarch64")
        self.assertEqual(f_osbit("linux", "i686"), "linux32")
        self.assertEqual(f_osbit("linux", "x86_64"), "linux64")
        self.assertEqual(f_osbit("freebsd", "x86_64"), "freebsd64")
        self.assertEqual(f_osbit("freebsd", "i686"), "freebsd32")

    def test_bit(self):
        self.assertEqual(f_bit("i686"), 32)
        self.assertEqual(f_bit("x86_64"), 64)
        self.assertEqual(f_bit("ARMv7"), 32)
        self.assertEqual(f_bit("ARMv8"), 64)

    def test_extension(self):
        self.assertEqual(f_extension("linux"), "tar.gz")
        self.assertEqual(f_extension("macos"), "dmg")
        self.assertEqual(f_extension("freebsd"), "tar.gz")
        self.assertEqual(f_extension("windows"), "exe")

    def test_latest_filename(self):
        info = generate_info("latest", "linux", "i686")
        self.assertEqual(info["latest_filename"],
                         "julia-latest-linux32.tar.gz")
        info = generate_info("latest", "linux", "x86_64")
        self.assertEqual(info["latest_filename"],
                         "julia-latest-linux64.tar.gz")

        info = generate_info("latest", "linux", "ARMv8")
        self.assertEqual(info["latest_filename"],
                         "julia-latest-linuxaarch64.tar.gz")

        info = generate_info("latest", "windows", "i686")
        self.assertEqual(info["latest_filename"],
                         "julia-latest-win32.exe")
        info = generate_info("latest", "windows", "x86_64")
        self.assertEqual(info["latest_filename"],
                         "julia-latest-win64.exe")

        info = generate_info("latest", "macos", "x86_64")
        self.assertEqual(info["latest_filename"],
                         "julia-latest-mac64.dmg")

    def test_filename(self):
        info = generate_info("1.3.0", "linux", "i686")
        self.assertEqual(info["filename"],
                         "julia-1.3.0-linux-i686.tar.gz")
        info = generate_info("1.3.0", "linux", "x86_64")
        self.assertEqual(info["filename"],
                         "julia-1.3.0-linux-x86_64.tar.gz")
        info = generate_info("1.3.0", "linux", "ARMv7")
        self.assertEqual(info["filename"],
                         "julia-1.3.0-linux-armv7l.tar.gz")
        info = generate_info("1.3.0", "linux", "ARMv8")
        self.assertEqual(info["filename"],
                         "julia-1.3.0-linux-aarch64.tar.gz")

        info = generate_info("1.3.0", "windows", "i686")
        self.assertEqual(info["filename"],
                         "julia-1.3.0-win32.exe")
        info = generate_info("1.3.0", "windows", "x86_64")
        self.assertEqual(info["filename"],
                         "julia-1.3.0-win64.exe")

        info = generate_info("1.3.0", "macos", "x86_64")
        self.assertEqual(info["filename"],
                         "julia-1.3.0-mac64.dmg")

        info = generate_info("1.3.0", "freebsd", "x86_64")
        self.assertEqual(info["filename"],
                         "julia-1.3.0-freebsd-x86_64.tar.gz")
