from .filters import is_valid_release
from .filters import is_system, is_architecture
from .filters import VALID_SYSTEM, VALID_ARCHITECTURE
from .filters import f_major_version, f_minor_version, f_patch_version
from .defaults import RELEASE_CONFIGFILE
from .sys_utils import current_system, current_architecture
from .sys_utils import show_verbose
from .interactive_utils import color

from .source_utils import SourceRegistry

import semantic_version

from itertools import product
import csv
import os
import logging

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
            version_string = Version.get_version(version_string)
            self.major_version = f_major_version(version_string)
            self.minor_version = f_minor_version(version_string)
            self.patch_version = f_patch_version(version_string)
        super(Version, self).__init__(version_string)

    # TODO: we can actually wrap latest_version here
    @staticmethod
    def get_version(version: str):
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


def read_releases(stable_only=False) -> List[Tuple]:
    """
    read release info from local storage
    """
    # TODO: read from versions.json (#16)
    cfg_file = RELEASE_CONFIGFILE
    if not os.path.isfile(cfg_file):
        return []
    with open(cfg_file, "r") as csvfile:
        releases = []
        for row in csv.reader(csvfile):
            releases.append(tuple(row))
    if stable_only:
        releases = list(filter(lambda x: x[0] != "latest",
                               releases))
    return releases


def is_version_released(version, system, architecture,
                        update=False,
                        upstream=None,
                        timeout=2,
                        cache=dict()):
    if not is_valid_release(version, system, architecture):
        return False

    if not cache:
        for item in read_releases():
            cache[item] = True

    item = str(version), system, architecture
    if item in cache:
        return cache[item]

    rst = False
    if update:
        # query process is time-consuming
        registry = SourceRegistry(upstream=upstream)
        rst = bool(registry.query_download_url(*item,
                                               timeout=timeout))
        if show_verbose():
            c = color.GREEN if rst else color.RED
            msg = f"{c}{item}={rst}{color.END}"
            print(msg)
        if rst:
            logging.info(f"get new release {item}")
            try:
                # TODO: put this line to the "right" place
                os.chmod(RELEASE_CONFIGFILE, mode=0o755)
                with open(RELEASE_CONFIGFILE, 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(item)
            except PermissionError:
                logging.debug(f"unable to modify {RELEASE_CONFIGFILE}")
        else:
            logging.debug(f"queried {item} = {rst}")
        # only update cache in update mode
        cache[item] = rst
    return rst


def _latest_version(next_version, version, system, architecture,
                    **kwargs) -> str:
    last_version = Version(version)
    if not is_version_released(last_version, system, architecture,
                               **kwargs):
        return str(last_version)

    while True:
        test_version = next_version(last_version)
        if is_version_released(test_version, system, architecture,
                               **kwargs):
            last_version = test_version
        else:
            return str(last_version)


def latest_patch_version(version, system, architecture, **kwargs) -> str:
    """
    return the latest X.Y.z version starting from input version X.Y
    """
    if version == "latest":
        return version

    return _latest_version(Version.next_patch,
                           str(version), system, architecture,
                           **kwargs)


def latest_minor_version(version, system, architecture, **kwargs) -> str:
    """
    return the latest X.y.z version starting from input version X
    """
    if version == "latest":
        return version

    latest_minor = _latest_version(Version.next_minor,
                                   version, system, architecture,
                                   **kwargs)
    latest_patch = latest_patch_version(latest_minor, system, architecture,
                                        **kwargs)
    return latest_patch


def latest_major_version(version, system, architecture, **kwargs) -> str:
    """
    return the latest x.y.z version
    """
    if version == "latest":
        return version

    latest_major = _latest_version(Version.next_major,
                                   version, system, architecture,
                                   **kwargs)
    latest_minor = _latest_version(Version.next_minor,
                                   latest_major, system, architecture,
                                   **kwargs)
    latest_patch = _latest_version(Version.next_patch,
                                   latest_minor, system, architecture,
                                   **kwargs)
    return latest_patch


def latest_version(version: str, system, architecture, update=True, **kwargs) -> str:
    """
    find the latest version for partial semantic version string. Directly
    return `version` if it's already a complete version string.
    """
    # supporting legacy versions is really of low priority
    if version and Version(version) < Version("0.6.0"):
        raise(ValueError('Julia < v"0.6.0" is not supported.'))

    # if user passes a complete version here, then we don't need to query
    # from local storage, just trying to download it would be fine.
    if is_full_version(version):
        return version

    if update:
        print(f"query the latest {version} version, it may take seconds...")
    if len(version.strip()) == 0:
        # if empty string is provided, query the latest version since the latest stable released
        # version. This version might not be released yet for specific platform, e.g., ARMv7, in
        # this case, we query the database and return the latest one
        versions = sorted(
            set(map(lambda x: x[0], read_releases(stable_only=True))), key=Version)
        ver = latest_major_version(
            max(versions), system, architecture, update=update, **kwargs)

        if is_version_released(ver, system, architecture, update=update, **kwargs):
            return ver
        else:
            for ver in reversed(versions):
                if is_version_released(ver, system, architecture, update=False, **kwargs):
                    if Version(ver) < Version(max(versions)):
                        print(
                            f'{color.YELLOW}failed to find version "{version}", fallback to "{ver}"{color.END}')
                    return ver
            print(
                f'{color.RED}failed to find latest version for "{version}"{color.END}')
            return max(versions)

    else:
        # TODO: we can also support ^ and > semantics here
        idx = len(version.split('.')) - 1
        f = [latest_minor_version, latest_patch_version][idx]
        ver = f(version, system, architecture,
                update=update, **kwargs)

        if is_version_released(ver, system, architecture, update=update, **kwargs):
            return ver
        else:
            f = [f_major_version, f_minor_version][idx]
            versions = sorted(
                [x[0] for x in read_releases(stable_only=True) if f(x[0]) == version], key=Version)
            for ver in versions:
                if is_version_released(ver, system, architecture, update=False, **kwargs):
                    if Version(ver) < Version(max(versions)):
                        version_str = version if version else "latest"
                        print(
                            f'{color.YELLOW}failed to find version "{version_str}", fallback to "{ver}"{color.END}')
                    return ver
                print(
                    f'{color.RED}failed to find latest version for "{version}"{color.END}')
                return max(versions)


def sort_releases():
    releases = read_releases()
    releases.sort(key=lambda x: (x[1], x[2], Version(x[0])))
    try:
        with open(RELEASE_CONFIGFILE, 'w') as csvfile:
            for item in releases:
                writer = csv.writer(csvfile)
                writer.writerow(item)
    except PermissionError:
        logging.debug(f"unable to modify {RELEASE_CONFIGFILE}")


def update_releases(system=None, architecture=None, *,
                    upstream="Official",
                    timeout=2):
    """
    check if there're new Julia releases

    Arguments:
      system: Options are:
        current system(default), SYSTEM, "all"
      architecture: Options are:
        current architecture(default), ARCHITECTURE, "all"
      upstream:
        manually choose a update upstream. By default it only checks
        from JuliaComputing's servers, i.e., "Official" upstream.
      timeout:
        how long each query waits before returning False
    """
    if system == "all":
        systems = VALID_SYSTEM
    else:
        system = system if system else current_system()
        is_system(system)
        systems = [system]

    if architecture == "all":
        architectures = VALID_ARCHITECTURE
    else:
        architecture = architecture if architecture else current_architecture()
        is_architecture(architecture)
        architectures = [architecture]

    # the first run gets all x.y.0 versions
    # the second run gets all x.y.z versions
    msg = "check new Julia release info, it will take a while"
    logging.info(msg)
    print(msg)
    kwargs = {
        "update": True,
        "upstream": upstream,
        "timeout": timeout
    }
    for _ in range(2):
        versions = set(map(lambda x: x[0], read_releases(stable_only=True)))
        versions = versions if len(versions) != 0 else {"0.6.0"}

        for item in product(versions, systems, architectures):
            # get all x.y.0 versions
            latest_major_version(*item, **kwargs)
            latest_minor_version(*item, **kwargs)
            latest_patch_version(*item, **kwargs)

    special_versions = ["latest"]
    for item in product(special_versions, systems, architectures):
        is_version_released(*item, **kwargs)

    sort_releases()
