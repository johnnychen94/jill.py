from .sys_utils import current_system
import os
import json

from typing import Dict

# this file isn't really a python script
# just some configuration constants
PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        ".."))


def get_configfiles(filename):
    """generate a list of config files ordered with their priorities"""
    configfile_list = []
    sys = current_system()
    if sys in ["macos", "freebsd", "linux"]:
        configfile_list.append(
            os.path.join(os.path.expanduser("~"),
                         ".config", "jill", filename)
        )
    elif sys == "windows":
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
