from .sys_utils import current_system
import os

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
RELEASE_CONFIGFILE = os.path.join(PKG_ROOT, "config", "releases.csv")
GPG_PUBLIC_KEY_PATH = os.path.join(PKG_ROOT, ".gnupg", "juliareleases.asc")

default_filename_template = "julia-$version-$osarch.$extension"
default_latest_filename_template = "julia-latest-$osbit.$extension"

# for mirror usage: where releases are downloaded to
default_path_template = "releases/$vminor_version/$filename"

# ports
default_scheme_ports = {
    "rsync": 873,
    "https": 443,
    "http": 80,
    "ftp": 21,
}
