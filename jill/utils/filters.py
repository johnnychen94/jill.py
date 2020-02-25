"""
Module `filters` defines placeholders and how names are filtered.
"""
from .defaults import default_filename_template
from .defaults import default_latest_filename_template

import re
from string import Template

from typing import Mapping, Optional, Callable

VERSION_REGEX = re.compile(
    r'v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(-(?P<status>\w+))?')
SPECIAL_VERSION_NAMES = ["latest", "nightly", "stable"]


rule_sys = {"windows": "winnt", "macos": "mac"}
rules_os = {"windows": "win", "macos": "mac"}
rules_arch = {
    "i686": "x86",
    "x86_64": "x64",
    "ARMv8": "aarch64",
    "ARMv7": "armv7l"
}
rules_osarch = {
    "win-i686": "win32",
    "win-x86_64": "win64",
    "mac-x86_64": "mac64",
    "linux-ARMv7": "linux-armv7l",
    "linux-ARMv8": "linux-aarch64"
}
rules_osbit = {
    "wini686": "win32",
    "winx86_64": "win64",
    "macx86_64": "mac64",
    "linuxARMv7": "linuxarmv7l",
    "linuxARMv8": "linuxaarch64",
    "linuxx86_64": "linux64",
    "linuxi686": "linux32",
    "freebsdx86_64": "freebsd64",
    "freebsdi686": "freebsd32"
}
rules_extension = {
    "windows": "exe",
    "linux": "tar.gz",
    "macos": "dmg",
    "freebsd": "tar.gz"
}
rules_bit = {
    "i686": 32,
    "x86_64": 64,
    "ARMv8": 64,
    "ARMv7": 32,
}

VALID_SYSTEM = ["windows", "linux", "freebsd", "macos"]
VALID_OS = ["win", "linux", "freebsd", "mac"]
VALID_ARCHITECTURE = list(rules_arch.keys())
VALID_ARCH = list(rules_arch.values())


def identity(*args):
    return args[0] if len(args) == 1 else args


def no_validate(*args, **kwargs):
    return True


def is_system(system):
    if system not in VALID_SYSTEM:
        err_msg = f"{system} isn't a valid system, "
        err_msg += f"possible choices are: {', '.join(VALID_SYSTEM)}"
        raise ValueError(err_msg)
    return True


def is_os(os):
    return os in VALID_OS


def is_architecture(arch):
    if arch not in VALID_ARCHITECTURE:
        err_msg = f"{arch} isn't a valid architecture, "
        err_msg += f"possible choices are: {', '.join(VALID_ARCHITECTURE)}"
        raise ValueError(err_msg)
    return True


def is_arch(arch):
    return arch in VALID_ARCH


def is_version(version):
    if version in SPECIAL_VERSION_NAMES:
        return True
    else:
        return bool(VERSION_REGEX.match(version))


def is_valid_release(version, system, architecture):
    if (system == "windows"
            and architecture not in ["i686", "x86_64"]):
        return False
    if (system == "macos"
            and architecture not in ["x86_64"]):
        return False
    if (system == "freebsd"
            and architecture not in ["x86_64"]):
        return False
    if (version == "latest" and (
            architecture not in ["i686", "x86_64"])):
        return False
    return True


class NameFilter:
    def __init__(self,
                 name: str,
                 f: Callable = identity,
                 rules: Optional[Mapping] = None,
                 validate: Callable = no_validate):
        self.f = f
        self.name = name
        self.rules = rules if rules else {}
        self.validate = validate

    def __call__(self, *args, **kwargs):
        if not self.validate(*args, **kwargs):
            # TODO: add error handler
            msg = f"validation on {self.name} fails:\n"
            msg += f"  - args: {args}\n  - kwargs: {kwargs}\n"
            msg += f"Please check if you have passed the right parameters"
            raise ValueError(msg)
        # directly return rst if there're no special filter rules
        rst = self.f(*args, **kwargs)
        return self.rules.get(rst, rst)


f_major_version = NameFilter("version", lambda x: x.lstrip('v').split('.')[0],
                             validate=is_version)
f_minor_version = NameFilter("version", lambda x: '.'.join(x.lstrip('v').
                                                           split('.')[0:2]),
                             validate=is_version)
f_patch_version = NameFilter("version", lambda x: x.lstrip('v').split('-')[0],
                             validate=is_version)


def _vmajor_version(ver):
    if ver in SPECIAL_VERSION_NAMES:
        return ver
    else:
        return 'v'+f_major_version(ver)


def _vminor_version(ver):
    if ver in SPECIAL_VERSION_NAMES:
        return ver
    else:
        return 'v'+f_minor_version(ver)


def _vpatch_version(ver):
    if ver in SPECIAL_VERSION_NAMES:
        return ver
    else:
        return 'v'+f_patch_version(ver)


def _version(ver):
    if ver in SPECIAL_VERSION_NAMES:
        return ver
    else:
        return ver.lstrip('v')


f_vmajor_version = NameFilter("version", _vmajor_version)
f_Vmajor_version = NameFilter(
    "version", lambda x: f_vmajor_version(x).capitalize())
f_vminor_version = NameFilter("version", _vminor_version)
f_Vminor_version = NameFilter(
    "version", lambda x: f_vminor_version(x).capitalize())
f_vpatch_version = NameFilter("version", _vpatch_version)
f_Vpatch_version = NameFilter(
    "version", lambda x: f_vpatch_version(x).capitalize())

f_version = NameFilter("version", _version, validate=is_version)

f_system = NameFilter("system", validate=is_system)
f_System = NameFilter("system", f=lambda x: f_system(x).capitalize())
f_SYSTEM = NameFilter("system", f=lambda x: f_system(x).upper())

f_sys = NameFilter("sys", rules=rule_sys, validate=is_system)
f_Sys = NameFilter("sys", f=lambda x: f_sys(x).capitalize())
f_SYS = NameFilter("sys", f=lambda x: f_sys(x).upper())

f_os = NameFilter("os", rules=rules_os, validate=is_system)
f_Os = NameFilter("os", f=lambda x: f_os(x).capitalize())
f_OS = NameFilter("os", f=lambda x: f_os(x).upper())

f_arch = NameFilter("arch", rules=rules_arch, validate=is_architecture)
f_Arch = NameFilter("arch", f=lambda x: f_arch(x).capitalize())
f_ARCH = NameFilter("arch", f=lambda x: f_arch(x).upper())

f_osarch = NameFilter("osarch", f=lambda os, arch: f"{os}-{arch}",
                      rules=rules_osarch,
                      validate=lambda os, arch:
                      is_os(os) and is_architecture(arch))


def _Osarch(os, arch):
    if os in ["win", "mac"]:
        return f_osarch(os, arch).capitalize()
    os, arch = f_osarch(os, arch).split('-')
    return os.capitalize() + '-' + arch


def _OSarch(os, arch):
    if os in ["win", "mac"]:
        return f_osarch(os, arch).upper()
    os, arch = f_osarch(os, arch).split('-')
    return os.upper() + '-' + arch


f_Osarch = NameFilter("osarch", _Osarch)
f_OSarch = NameFilter("osarch", _OSarch)

f_osbit = NameFilter("osbit", f=lambda os, arch: f"{os}{arch}",
                     rules=rules_osbit,
                     validate=lambda os, arch:
                     is_os(os) and is_architecture(arch))

f_bit = NameFilter("bit", rules=rules_bit, validate=is_architecture)

f_extension = NameFilter(
    "extension", rules=rules_extension, validate=is_system)


def _meta_filename(t, *args, **kwargs):
    if not isinstance(t, Template):
        t = Template(t)
    return t.substitute(*args, **kwargs)


def _filename(*args, **kwargs):
    return _meta_filename(default_filename_template, *args, **kwargs)


def _latest_filename(**kwargs):
    return _meta_filename(default_latest_filename_template, **kwargs)


f_filename = NameFilter("filename", _filename)
f_latest_filename = NameFilter("filename", _latest_filename)


def generate_info(plain_version: str,
                  system: str,
                  architecture: str,
                  **kwargs):
    os = f_os(system)
    arch = f_arch(architecture)

    configs = {}
    configs.update(kwargs)

    configs.update({
        "system": system,
        "System": f_System(system),
        "SYSTEM": f_SYSTEM(system),

        "sys": f_sys(system),
        "Sys": f_Sys(system),
        "SYS": f_SYS(system),

        "os": os,
        "Os": f_Os(system),
        "OS": f_OS(system),

        "architecture": architecture,

        "Arch": f_Arch(architecture),
        "arch": arch,
        "ARCH": f_ARCH(architecture),

        "osarch": f_osarch(os, architecture),
        "Osarch": f_Osarch(os, architecture),
        "OSarch": f_OSarch(os, architecture),

        "osbit": f_osbit(os, architecture),

        "bit": f_bit(architecture),
        "extension": f_extension(system),

        "version": f_version(plain_version),
        "major_version": f_major_version(plain_version),
        "vmajor_version": f_vmajor_version(plain_version),
        "minor_version": f_minor_version(plain_version),
        "vminor_version": f_vminor_version(plain_version),
        "patch_version": f_patch_version(plain_version),
        "vpatch_version": f_vpatch_version(plain_version)
    })

    configs.update({
        "filename": f_filename(**configs),
        "latest_filename": f_latest_filename(**configs)
    })

    return configs
