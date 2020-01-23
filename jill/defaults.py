from .sys_utils import current_system
import os

PKG_ROOT = os.path.abspath(os.path.dirname(__file__))


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
        # TODO: add user config file for windows
        pass

    # fallback config
    configfile_list.append(os.path.join(PKG_ROOT, "config", filename))
    return configfile_list


SOURCE_CONFIGFILE = get_configfiles("sources.json")
RELEASE_CONFIGFILE = os.path.join(PKG_ROOT, "config", "releases.csv")


default_filename_template = "julia-$patch_version-$osarch.$extension"
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
