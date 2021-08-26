from .sys_utils import current_system
import os
import json
import getpass

from typing import Dict

# this file isn't really a python script
# just some configuration constants
PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        ".."))


def get_configfiles(filename):
    """generate a list of config files ordered with their priorities"""
    configfile_list = []
    sys = current_system()
    if sys in ["mac", "freebsd", "linux"]:
        configfile_list.append(
            os.path.join(os.path.expanduser("~"),
                         ".config", "jill", filename)
        )
    elif sys == "winnt":
        configfile_list.append(
            os.path.join(os.path.expanduser(r"~\AppData\Local\julias"),
                         filename)
        )

    # fallback config
    configfile_list.append(os.path.join(PKG_ROOT, "config", filename))
    return configfile_list


SOURCE_CONFIGFILE = get_configfiles("sources.json")
GPG_PUBLIC_KEY_PATH = os.path.join(PKG_ROOT, ".gnupg", "juliareleases.asc")
DEFAULT_VERSIONS_URL = "https://julialang-s3.julialang.org/bin/versions.json"
VERSIONS_SCHEMA_URL = "https://julialang-s3.julialang.org/bin/versions-schema.json"

# for mirror usage: where releases are downloaded to
default_path_template = "releases/$vminor_version/$filename"


def default_depot_path():
    return os.environ.get("JULIA_DEPOT_PATH", os.path.expanduser("~/.julia"))


def default_symlink_dir():
    dir = os.environ.get("JILL_SYMLINK_DIR", None)
    if dir:
        return os.path.expanduser(dir)

    system = current_system()
    if system == "winnt":
        return os.path.expanduser(r"~\AppData\Local\julias\bin")
    if getpass.getuser() == "root":
        # available to all users
        return "/usr/local/bin"
    else:
        # exclusive to current user
        return os.path.expanduser("~/.local/bin")


def default_install_dir():
    dir = os.environ.get("JILL_INSTALL_DIR", None)
    if dir:
        return os.path.expanduser(dir)

    system = current_system()
    if system == "mac":
        return "/Applications"
    elif system in ["linux", "freebsd"]:
        if getpass.getuser() == "root":
            return "/opt/julias"
        else:
            return os.path.expanduser("~/packages/julias")
    elif system == "winnt":
        return os.path.expanduser(r"~\AppData\Local\julias")
    else:
        raise ValueError(f"Unsupported system: {system}")


def load_versions_schema(download=False, cache=dict()) -> Dict:
    """
        Load the schema configs.

        The schema is used to validate if the downloaded `versions.json` are valid.
    """
    configfile = os.path.join(PKG_ROOT, "config", "versions-schema.json")
    # Avoid unnecessary IO reads by caching the content into memeory
    if not cache:
        with open(configfile, "r") as file:
            schema = json.load(file)
        cache.update(schema)
    return cache


def load_alias(cache=dict()) -> Dict:
    """
        Load the alias configs.

        For better user experiences, jill allows alias for some os/arch, e.g., `windows`->`winnt`.
    """
    configfile = os.path.join(PKG_ROOT, "config", "alias.json")
    # Avoid unnecessary IO reads by caching the content into memeory
    if not cache:
        with open(configfile, "r") as file:
            alias = json.load(file)
        cache.update(alias)
    return cache


def load_placeholder(
        cache=dict()) -> Dict:
    """
        Load the placeholder configs.

        Placeholders are used to generate URLs from given template, see also "sources.json"
        for an example.
    """
    # Avoid unnecessary IO reads by caching the content into memeory
    configfile = os.path.join(PKG_ROOT, "config", "placeholders.json")
    if not cache:
        with open(configfile, "r") as file:
            schema = json.load(file)
        cache.update(schema)
    return cache


default_filename_template = "julia-$version-$osarch.$extension"
default_latest_filename_template = "julia-latest-$osbit.$extension"

# ports
default_scheme_ports = {
    "rsync": 873,
    "https": 443,
    "http": 80,
    "ftp": 21,
}
