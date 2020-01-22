import os

PKG_ROOT = os.path.abspath(os.path.dirname(__file__))
SOURCE_CONFIGFILE = os.path.join(PKG_ROOT, "config", "sources.json")
MIRROR_CONFIGFILE = os.path.join(PKG_ROOT, "config", "mirror.json")
RELEASE_CONFIGFILE = os.path.join(PKG_ROOT, "config", "releases.csv")

default_filename_template = "julia-$patch_version-$osarch.$extension"
default_latest_filename_template = "julia-latest-$osbit.$extension"

# for mirror usage: where releases are downloaded to
default_path_template = "releases/$sys/$arch/$minor_version/$filename"

# ports
default_scheme_ports = {
    "rsync": 873,
    "https": 443,
    "http": 80,
    "ftp": 21,
}
