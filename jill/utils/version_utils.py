from .filters import is_valid_release
from .filters import is_system, is_architecture
from .filters import VALID_SYSTEM, VALID_ARCHITECTURE
from .filters import f_major_version, f_minor_version, f_patch_version
from .defaults import VERSIONS_URL
from .sys_utils import current_system, current_architecture
from .sys_utils import show_verbose
from .interactive_utils import color

from .source_utils import SourceRegistry

import semantic_version

from itertools import product
import csv
import os
import logging
import requests
import json

from typing import Tuple, List


def is_full_version(version: str):
    if version == "latest":
        return True
    try:
        semantic_version.Version(version)
    except ValueError:
        return False
    return True


class Version(semantic_version.Version):
    """
    a thin wrapper on semantic_version.Version that

    * accepts "latest"
    * accepts partial version, e.g., `1`, `1.0`
    """

    def __init__(self, version_string):
        if version_string == "latest":
            version_string = "999.999.999"
            self.major_version = "latest"
            self.minor_version = "latest"
            self.patch_version = "latest"
        else:
            version_string = Version.get_full_version(version_string)
            self.major_version = f_major_version(version_string)
            self.minor_version = f_minor_version(version_string)
            self.patch_version = f_patch_version(version_string)
        super(Version, self).__init__(version_string)

    # TODO: we can actually wrap latest_version here
    @staticmethod
    def get_full_version(version: str):
        """
        add trailing 0s for incomplete version string
        """
        splited = str(version).split(".")
        if len(splited) == 1:
            major, minor, patch = splited[0], "0", "0"
        elif len(splited) == 2:
            major, minor = splited[0:2]
            patch = "0"
        elif len(splited) == 3:
            major, minor, patch = splited[0:3]
        else:
            raise ValueError(f"Unrecognized version string {version}")
        return ".".join([major, minor, patch])


def cache_read_remote_json(url, cache=dict()):
    """
        If not cached, download and read json content from remote URL `url`.
    """
    if not cache:
        print(
            f'{color.GREEN}querying release information (from julialang-s3.julialang.org){color.END}')
        cache.update(json.loads(requests.get(url).text))
    return cache


def read_releases(stable_only=False) -> List[Tuple]:
    """
    read release info from versions.json (VERSIONS_URL)
    The content will be cached so will only download the data once.
    """
    # Here we only cache the raw content so that post processing like `stable_only` filter
    # works as expected.
    v = cache_read_remote_json(VERSIONS_URL)
    releases = []
    for item in v.items():
        ver = item[0]
        is_stable = item[1]['stable']
        if not stable_only or is_stable:
            files = item[1]['files']
            for file in files:
                # TODO: Use inverse filters here instead of hardcoding....
                os = file['os']
                if os == 'winnt':
                    system = 'windows'
                elif os == 'mac':
                    system = 'macos'
                elif os == 'linux' and file["triplet"][-4:] == 'musl':
                    system = 'musl'
                else:
                    system = os

                arch = file['arch']
                if arch == 'aarch64':
                    arch = 'ARMv8'
                elif arch == 'armv7l':
                    arch = 'ARMv7'

                releases.append((ver, system, arch))
    return releases  # type: ignore


def is_version_released(version, system, architecture, stable_only=False):
    """
        Checks if the given version number is released for the given system and architecture.
        Note: returns True for version="latest" if system and architecture are valid.
    """
    if not is_valid_release(version, system, architecture):
        return False

    # special case version="latest"
    if version == "latest":
        return True

    version_list = read_releases(stable_only=stable_only)
    item = str(version), system, architecture
    return (item in version_list)


def latest_version(version: str, system, architecture, stable_only=True, **kwargs) -> str:
    """
    Autocompletes a partial semantic version string to the latest compatible full version string.
    Directly returns `version` if it's already a complete version string (without checking that it's
    a valid one).
    """
    # supporting legacy versions is really of low priority
    if version and Version(version) < Version("0.6.0"):
        raise(ValueError('Julia < v"0.6.0" is not supported.'))

    # Download whatever the user requests; ignores `stable_only`.
    if is_full_version(version):
        return version

    # query system/architecture-compatible releases
    releases = read_releases(stable_only=stable_only)
    compat_releases = list(filter(lambda x: x[1] == system and x[2] == architecture, releases))
    if len(compat_releases) == 0:
        latest_ver = max(releases, key=lambda x: Version(x[0]))[0]
        print(
            f'{color.RED}failed to find latest Julia version for "{system}" and "{architecture}". Trying latest compatible version "{latest_ver}" instead.{color.END}')
        return latest_ver

    if len(version.strip()) == 0:
        # version is an empty string => try to find latest compatible release
        return max(compat_releases, key=lambda x: Version(x[0]))[0]

    else:
        filtered_compat = list(filter(lambda x: x[0].startswith(version), compat_releases))
        if len(filtered_compat) == 0:
            latest_ver = max(compat_releases, key=lambda x: Version(x[0]))[0]
            print(
                f'{color.RED}failed to find latest Julia version for "{version}", "{system}" and "{architecture}". Trying latest compatible version "{latest_ver}" instead.{color.END}')
            return latest_ver
        else:
            latest_compat = max(filtered_compat, key=lambda x: Version(x[0]))
            return latest_compat[0]
