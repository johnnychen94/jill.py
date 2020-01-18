import os

PKG_ROOT = os.path.abspath(os.path.dirname(__file__))
SOURCE_CONFIGFILE = os.path.join(PKG_ROOT, "config", "sources.json")

# upstream url
fb_prefix = 'https://julialang-s3.julialang.org/bin/'
fb_nightly_prefix = 'https://julialangnightlies-s3.julialang.org/bin/'
fb_nightly_url_template = fb_nightly_prefix + '$sys/$arch/$filename'
fb_release_url_template = fb_prefix + '$sys/$arch/$minor_version/$filename'
fb_md5_template = fb_prefix + 'checksums/julia-$patch_version.md5'
fb_sha256_template = fb_prefix + 'julia-$patch_version.sha256'

default_filename_template = "julia-$patch_version-$osarch.$extension"
default_latest_filename_template = "julia-latest-$os$bit.$extension"

# for mirror usage: where releases are downloaded to
default_path_template = "releases/$sys/$arch/$minor_version/$filename"

# ports
default_scheme_ports = {
    "rsync": 873,
    "https": 443,
    "http": 80,
    "ftp": 21,
}
