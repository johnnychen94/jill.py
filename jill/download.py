from .utils import SourceRegistry, verify_upstream
from .utils import latest_version
from .utils import is_version_released
from .utils import is_full_version
from .utils import current_system, current_architecture, current_libc
from .utils import verify_gpg
from .utils import color
from .utils.filters import canonicalize_sys, canonicalize_arch

import wget
import os
import shutil
import tempfile
import logging

from urllib.parse import urlparse

from typing import Optional

from urllib.error import URLError


def _download(url: str, out: str):
    # always do overwrite
    outpath = os.path.abspath(out)
    outdir, outname = os.path.split(outpath)

    with tempfile.TemporaryDirectory() as temp_outdir:
        temp_outpath = os.path.join(temp_outdir, outname)
        try:
            msg = f"downloading from {url}"
            logging.info(msg)
            print(msg)
            wget.download(url, temp_outpath)
            print()  # for format usage
            msg = f"finished downloading {outname}"
            print(f"{color.GREEN}{msg}{color.END}")
        except (URLError, ConnectionError):
            msg = f"failed to download {outname}"
            logging.info(msg)
            print(f"{color.RED}{msg}{color.END}")
            return False

        if not os.path.isdir(outdir):
            os.makedirs(outdir, exist_ok=True)
        shutil.move(temp_outpath, outpath)

    return outpath


def download_package(version=None, sys=None, arch=None, *,
                     upstream=None,
                     outdir=None,
                     overwrite=False):
    """
    download julia release from nearest servers

    `jill download [version] [sys] [arch]` downloads a Julia release
    in your current folder. If you don't specify any argument, then
    it will download the latest stable version for your current platform.

    The syntax for `version` is:

    * `stable`: latest stable Julia release. This is the _default_ option.
    * `1`: latest `1.y.z` Julia release.
    * `1.0`: latest `1.0.z` Julia release.
    * `1.4.0-rc1`: as it is. This is the only way to install unstable release.
    * `latest`/`nightly`: the nightly builds from source code.

    For whatever reason, if you only want to download release from
    a specific upstream (e.g., from JuliaComputing), then you can use
    `--upstream` flag (e.g., `jill download --upstream Official`).

    To see a full list of upstream servers, please use `jill upstream`.

    If you're interested in downloading from an unregistered private
    mirror, you can provide a `sources.json` file to CONFIG_PATH and use
    `jill upstream` to check if your mirror is added. A config template
    can be found at [1].

    CONFIG_PATH:
      * windows: `~\\AppData\\Local\\julias\\sources.json`
      * other: `~/.config/jill/sources.json`

    [1]: https://github.com/johnnychen94/jill.py/blob/master/jill/config/sources.json # nopep8

    Arguments:
      version:
        The Julia version you want to install. See also `jill install`
      sys: Options are: "linux", "musl", "macos", "freebsd", "windows"/"winnt"/"win"
      arch: Options are: "i686"/"x86", "x86_64"/"x64", "ARMv7"/"armv7l", "ARMv8"/"aarch64"
      upstream:
        manually choose a download upstream. For example, set it to "Official"
        if you want to download from JuliaComputing's s3 buckets.
      outdir:
        where release is downloaded to. By default it's the current folder.
      overwrite:
        add `--overwrite` flag to overwrite existing releases.
    """
    version = str(version) if (version or str(version) == "0") else ""
    version = "latest" if version == "nightly" else version
    version = "" if version == "stable" else version
    upstream = upstream if upstream else os.environ.get("JILL_UPSTREAM", None)

    system = sys if canonicalize_sys(sys) else current_system()
    if system == "linux" and current_system() == "linux" and current_libc() == "musl":
        # currently Julia tags musl as a system, e.g.,
        # https://julialang-s3.julialang.org/bin/musl/x64/1.5/julia-1.5.1-musl-x86_64.tar.gz
        system = "musl"
    architecture = arch if canonicalize_arch(arch) else current_architecture()

    # allow downloading unregistered releases, e.g., 1.4.0-rc1
    do_release_check = not is_full_version(version)

    if upstream:
        verify_upstream(upstream)
    wrong_args = False
    try:
        version = latest_version(
            version, system, architecture, upstream=upstream)
    except ValueError:
        # hide the nested error stack :P
        wrong_args = True
    if wrong_args:
        msg = f"something wrong for the platform argument you passed:\n"
        msg += f"  - version(>= 0.6.0): {version}\n"
        msg += f"  - system: {system}\n"
        msg += f"  - archtecture: {architecture}\n"
        msg += f"example: `jill download 1 linux x86_64`"
        raise(ValueError(msg))

    release_str = f"{version}-{system}-{architecture}"
    if do_release_check:
        rst = is_version_released(
            version, system, architecture, upstream=upstream)
        if not rst:
            msg = f"failed to find {release_str} in available upstream. Please try it later."
            logging.info(msg)
            print(f"{color.RED}{msg}{color.END}")
            return False

    msg = f"downloading Julia release for {release_str}"
    logging.info(msg)
    print(msg)
    registry = SourceRegistry(upstream=upstream)
    url = registry.query_download_url(version, system, architecture)
    if not url:
        msg = f"failed to find {release_str} in available upstream. Please try it later."
        logging.warning(msg)
        print(f"{color.RED}{msg}{color.END}")
        return None

    outdir = outdir if outdir else '.'
    outdir = os.path.abspath(outdir)
    if current_system() == "windows":
        outdir = outdir.replace("\\\\", "\\")

    outname = os.path.split(urlparse(url).path)[1]
    outpath = os.path.join(outdir, outname)

    skip_download = False
    if system in ["linux", "freebsd"]:
        if (os.path.isfile(outpath) and os.path.isfile(outpath+".asc")
                and not overwrite):
            skip_download = True
    else:
        if os.path.isfile(outpath) and not overwrite:
            skip_download = True
    if skip_download:
        msg = f"{outname} already exists, skip downloading"
        logging.info(msg)
        print(f"{color.GREEN}{msg}{color.END}")
        return outpath

    package_path = _download(url, outpath)

    if system in ["winnt", "mac"]:
        # macOS and Windows releases are codesigned with certificates
        # that are verified by the operating system during installation
        return package_path
    elif system in ["linux", "freebsd", "musl"]:
        # need additional verification using GPG
        if not package_path:
            return package_path

        # a mirror should provides both *.tar.gz and *.tar.gz.asc
        gpg_signature_path = _download(url+".asc", outpath+".asc")
        if not gpg_signature_path:
            msg = f"failed to download GPG signature for {release_str}\n"
            msg += "remove untrusted/broken file"
            logging.info(msg)
            print(f"{color.RED}{msg}{color.END}")
            os.remove(package_path)
            return False

        if not verify_gpg(package_path, gpg_signature_path):
            msg = f"failed to verify {release_str} downloads\n"
            msg += "remove untrusted/broken files"
            logging.info(msg)
            print(f"{color.RED}{msg}{color.END}")
            os.remove(package_path)
            os.remove(gpg_signature_path)
            return False

        # GPG-verified julia release path
        msg = f"verifying {release_str} succeed"
        logging.info(msg)
        print(f"{color.GREEN}{msg}{color.END}")
        return package_path
    else:
        os.remove(package_path)
        raise ValueError(f"unsupported system {sys}")
