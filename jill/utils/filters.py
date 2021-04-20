"""
Module `filters` defines placeholders and how names are filtered.
"""
from .defaults import default_filename_template
from .defaults import default_latest_filename_template
from .defaults import load_placeholder, load_alias

import re
from string import Template

from typing import Mapping, Optional, Callable

VERSION_REGEX = re.compile(
    r'v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(-(?P<status>\w+))?')
SPECIAL_VERSION_NAMES = ["latest", "nightly", "stable"]


def is_version(version):
    if version in SPECIAL_VERSION_NAMES:
        return True
    else:
        return bool(VERSION_REGEX.match(version))


def canonicalize_arch(arch: Optional[str]):
    """
        Canonicalize arch names to arch names defined by Julia schema.

        For example, `--sys=win` is allowed in jill but this is
        not listed in Julia's `versions-schema.json`. This function
        maps these alias into the legal names defined by
        `versions-schema.json`.

        The canonicalize rule is defined in `jill/config/alias.json`, for
        names not in that list, it's an identity map.
    """
    if arch is not None:
        return load_alias()["Arch"].get(arch.lower(), arch.lower())


def canonicalize_sys(os: Optional[str]):
    """
        Canonicalize sys names to OS names defined by Julia schema.

        For example, `--sys=win` is allowed in jill but this is
        not listed in Julia's `versions-schema.json`. This function
        maps these alias into the legal names defined by
        `versions-schema.json`.

        The canonicalize rule is defined in `jill/config/alias.json`, for
        names not in that list, it's an identity map.
    """
    if os is not None:
        return load_alias()["OS"].get(os.lower(), os.lower())


def identity(*args):
    return args[0] if len(args) == 1 else args


def no_validate(*args, **kwargs):
    return True


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


class NameFilter:
    def __init__(self,
                 name: str,
                 f: Callable = identity,
                 rules: Optional[Mapping] = None,
                 validate: Callable = no_validate):
        self.f = f
        self.name = name
        if rules:
            self.rules = rules
        else:
            rules = load_placeholder().get(name, dict())
            self.rules = rules if rules else dict()
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


f_system = NameFilter("system")
f_System = NameFilter("system", f=lambda x: f_system(x).capitalize())
f_SYSTEM = NameFilter("system", f=lambda x: f_system(x).upper())

f_sys = NameFilter("sys")
f_Sys = NameFilter("sys", f=lambda x: f_sys(x).capitalize())
f_SYS = NameFilter("sys", f=lambda x: f_sys(x).upper())

f_os = NameFilter("os")
f_Os = NameFilter("os", f=lambda x: f_os(x).capitalize())
f_OS = NameFilter("os", f=lambda x: f_os(x).upper())

f_arch = NameFilter("arch")
f_Arch = NameFilter("arch", f=lambda x: f_arch(x).capitalize())
f_ARCH = NameFilter("arch", f=lambda x: f_arch(x).upper())

f_osarch = NameFilter("osarch", f=lambda os, arch: f"{os}-{arch}")
f_Osarch = NameFilter("osarch", f=_Osarch)
f_OSarch = NameFilter("osarch", f=_OSarch)

f_osbit = NameFilter("osbit", f=lambda os, arch: f"{os}{arch}")
f_bit = NameFilter("bit")
f_extension = NameFilter("extension")


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
    system = canonicalize_sys(system)
    architecture = canonicalize_arch(architecture)

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
