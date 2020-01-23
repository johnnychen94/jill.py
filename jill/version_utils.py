from .source import SourceRegistry
from .filters import is_valid_release
from .filters import SPECIAL_VERSION_NAMES
from .filters import is_system, is_architecture
from .filters import VALID_SYSTEM, VALID_ARCHITECTURE
from .defaults import RELEASE_CONFIGFILE
from .sys_utils import current_system, current_architecture
from semantic_version import Version

from itertools import product
import csv
import os
import logging

from typing import Tuple, List


def read_releases(stable_only=False) -> List[Tuple]:
    cfg_file = RELEASE_CONFIGFILE
    if not os.path.isfile(cfg_file):
        return []
    with open(cfg_file, "r") as csvfile:
        releases = []
        for row in csv.reader(csvfile):
            releases.append(tuple(row))
    if stable_only:
        releases = list(filter(lambda x: x[0] not in SPECIAL_VERSION_NAMES,
                               releases))
    return releases


def is_version_released(version, system, architecture,
                        update=False,
                        upstream=None,
                        timeout=5,
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
                                               timeout=timeout,
                                               max_try=1))
        if rst:
            logging.info(f"get new release {item}")
            with open(RELEASE_CONFIGFILE, 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(item)
        else:
            logging.debug(f"queried {item} = {rst}")
        # only update cache in update mode
        cache[item] = rst
    return rst


def get_version(version: str):
    """
    add tailing 0s for incomplete version string
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
    return Version(".".join([major, minor, patch]))


def _latest_version(next_version, version, system, architecture,
                    **kwargs) -> str:
    last_version = get_version(version)
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
    return the latest X.Y.z version starting from input version X.Y.Z
    """
    return _latest_version(Version.next_patch,
                           str(version), system, architecture,
                           **kwargs)


def latest_minor_version(version, system, architecture, **kwargs) -> str:
    """
    return the latest X.y.z version starting from input version X.Y.Z
    """
    latest_minor = _latest_version(Version.next_minor,
                                   version, system, architecture,
                                   **kwargs)
    latest_patch = latest_patch_version(latest_minor, system, architecture,
                                        **kwargs)
    return latest_patch


def latest_major_version(version, system, architecture, **kwargs) -> str:
    """
    return the latest x.y.z version starting from input version X.Y.Z
    """
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


def latest_version(version, system, architecture, **kwargs) -> str:
    """
    find the latest version for partial semantic version string. Directly
    return `version` if it's already a complete version string.
    """
    if version in SPECIAL_VERSION_NAMES:
        return version

    f_list = [latest_minor_version,
              latest_patch_version]
    f_list.append(lambda ver, sys, arch, **kwargs: ver)  # type: ignore

    if len(version) == 0:
        return latest_major_version('1', system, architecture, **kwargs)
    else:
        idx = len(version.split('.')) - 1
        return f_list[idx](version, system, architecture, **kwargs)


def _make_version(ver: str) -> Version:
    if ver == "latest":
        ver = "999.999.999"
    return Version(ver)


def sort_releases():
    releases = read_releases()
    releases.sort(key=lambda x: (x[1], x[2], _make_version(x[0])))
    with open(RELEASE_CONFIGFILE, 'w') as csvfile:
        for item in releases:
            writer = csv.writer(csvfile)
            writer.writerow(item)


def update_releases(system=None, architecture=None, *,
                    upstream="Official",
                    timeout=5):
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
    logging.info("check new Julia release info, it will take a while")
    kwargs = {
        "update": True,
        "upstream": upstream,
        "timeout": timeout
    }
    for _ in range(2):
        versions = set(map(lambda x: x[0], read_releases(stable_only=True)))
        versions = versions if len(versions) != 0 else {"1.0.0"}

        for item in product(versions, systems, architectures):
            # get all x.y.0 versions
            latest_major_version(*item, **kwargs)
            latest_minor_version(*item, **kwargs)
            latest_patch_version(*item, **kwargs)

    special_versions = ["latest"]
    for item in product(special_versions, systems, architectures):
        is_version_released(*item, **kwargs)

    sort_releases()
