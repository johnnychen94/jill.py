from .filters import f_major_version, f_minor_version, f_patch_version
from .filters import canonicalize_arch, canonicalize_sys
from .defaults import load_versions_schema
from .defaults import DEFAULT_VERSIONS_URL, VERSIONS_SCHEMA_URL
from .net_utils import first_response
from .source_utils import read_registry
from .interactive_utils import color
import semantic_version

import requests
import json
import jsonschema

from jsonschema.exceptions import ValidationError
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


def read_remote_versions(upstream, cache=dict()):
    """
        If not cached, download and read json content from remote URL `url`.
    """
    if not cache:
        registry = read_registry()
        if upstream in registry:
            versions_url = registry[upstream].versions_url
        else:
            # If not specified, use the first response as the result
            # TODO: we can share the first_response result here so that later
            #       downloading (e.g., `query_download_url`) does not need to check
            #       it again.
            versions_url_list = [x.versions_url for x in registry.values()]
            versions_url = first_response(versions_url_list, timeout=0.5)
            versions_url = versions_url if versions_url else DEFAULT_VERSIONS_URL
        print(
            f'{color.GREEN}querying release information from {versions_url}{color.END}')
        version_list = json.loads(requests.get(versions_url).text)

        # Validate the downloaded content with `versions_schema.json`.
        # This file is unlikely to be outdated so we keep a copy
        # inside `jill`. If it gets outdated, then print a warning message and
        # download the lastest schema file.
        # When there're new arch/sys that makes this our copy outdated, it's very
        # likely that `jill` doesn't support it.
        schema = load_versions_schema()
        try:
            jsonschema.validate(version_list, schema)
            is_valid = True
        except ValidationError:
            is_valid = False
            print(
                f'{color.YELLOW} failed to validate versions file, retry with latest schema...')
            schema = json.load(requests.get(VERSIONS_SCHEMA_URL).text)
        if not is_valid:
            jsonschema.validate(version_list, schema)

        cache.update(version_list)
    return cache


def read_releases(minimal_version='0.6.0', stable_only=False, upstream=None) -> List[Tuple[str, str, str]]:
    """
    read release info from versions.json.
    The content will be cached so will only download the data once.
    """
    # Here we only cache the raw content so that post processing like `stable_only` filter
    # works as expected.
    v = read_remote_versions(upstream=upstream)
    releases = []
    for item in v.items():
        ver = item[0]
        is_stable = item[1]['stable']
        if not stable_only or is_stable:

            # minimal_version works only when is_stable=True
            try:
                # TODO: a cleaner solution
                if Version(ver) < Version(minimal_version):
                    continue
            except:
                continue

            files = item[1]['files']
            for file in files:
                os = file['os']
                libc = file['triplet'].split('-')[2]
                if libc == "musl":
                    # currently Julia tags musl as a system, e.g.,
                    # https://julialang-s3.julialang.org/bin/musl/x64/1.5/julia-1.5.1-musl-x86_64.tar.gz
                    os = "musl"
                releases.append((ver, os, file['arch']))
    return releases


def is_version_released(version, system, arch, **kwargs):
    """
        Checks if the given version number is released for the given system and architecture.
        Note: returns True for version="latest" if system and architecture are valid.
    """
    # special case version="latest"
    if version == "latest":
        # All the new stuff in nightly builds might break the schema check, thus we directly
        # return True here without any extra checks.
        return True

    version_list = read_releases(**kwargs)
    item = str(version), canonicalize_sys(system), canonicalize_arch(arch)
    return (item in version_list)


def latest_version(version: str, system, arch, **kwargs) -> str:
    """
    Autocompletes a partial semantic version string to the latest compatible full version string.
    Directly returns `version` if it's already a complete version string (without checking that it's
    a valid one).
    """
    system, arch = canonicalize_sys(system), canonicalize_arch(arch)
    # supporting legacy versions is really of low priority
    if version and Version(version) < Version("0.6.0"):
        raise(ValueError('Julia < v"0.6.0" is not supported.'))

    # Download whatever the user requests; ignores `stable_only`.
    if is_full_version(version):
        return version

    # query system/architecture-compatible releases
    releases = read_releases(**kwargs)
    compat_releases = [x for x in releases if x[1] == system and x[2] == arch]
    if len(compat_releases) == 0:
        raise(ValueError(
            f'Julia release for system {system} and architecture {arch} is not available.'))

    if len(version.strip()) == 0:
        # version is an empty string => try to find latest compatible release
        return max(compat_releases, key=lambda x: Version(x[0]))[0]
    else:
        filtered_compat = [
            x for x in compat_releases if x[0].startswith(version)]
        if len(filtered_compat) == 0:
            latest_ver = max(compat_releases, key=lambda x: Version(x[0]))[0]
            print(f'{color.RED}failed to find latest Julia version for "{version}", "{system}" and "{arch}". Trying latest compatible version "{latest_ver}" instead.{color.END}')
            # This is equivalent to:
            # latest_version('', system, arch, stable_only=stable_only)
            return latest_ver
        else:
            latest_compat = max(filtered_compat, key=lambda x: Version(x[0]))
            return latest_compat[0]
