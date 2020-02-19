from .utils import SourceRegistry
from .utils import latest_version
from .utils import is_version_released
from .utils import is_full_version
from .utils import current_system, current_architecture
from .utils import verify_gpg

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
            logging.info(f"downloading source: {url}")
            wget.download(url, temp_outpath)
            print()  # for format usage
            logging.info(f"finished downloading {outname}")
        except (URLError, ConnectionError) as e:
            logging.warning(f"failed to download {outname}")
            return False

        if not os.path.isdir(outdir):
            os.makedirs(outdir, exist_ok=True)
        shutil.move(temp_outpath, outpath)

    return outpath


def download_package(version=None, sys=None, arch=None, *,
                     upstream=None,
                     outdir=None,
                     overwrite=False,
                     max_try=3):
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
    can be found at [1]. For how to make such mirror, please refer to
    `jill mirror`.

    CONFIG_PATH:
      * windows: `~\\AppData\\Local\\julias\\sources.json`
      * other: `~/.config/jill/sources.json`

    [1]: https://github.com/johnnychen94/jill.py/blob/master/jill/config/sources.json # nopep8

    Arguments:
      version:
        The Julia version you want to install. See also `jill install`
      sys: Options are: "linux", "macos", "freebsd", "windows"
      arch: Options are: "i686", "x86_64", "ARMv7", "ARMv8"
      upstream:
        manually choose a download upstream. For example, set it to "Official"
        if you want to download from JuliaComputing's s3 buckets.
      outdir:
        where release is downloaded to. By default it's the current folder.
      overwrite:
        add `--overwrite` flag to overwrite existing releases.
      max_try:
        try `max_try` times before returning a False. The default value is 3.
    """
    version = str(version) if version else ""
    version = "latest" if version == "nightly" else version
    version = "" if version == "stable" else version

    system = sys if sys else current_system()
    architecture = arch if arch else current_architecture()

    # allow downloading unregistered releases, e.g., 1.4.0-rc1
    do_release_check = not is_full_version(version)
    version = latest_version(version, system, architecture)

    if architecture in ["ARMv7", "ARMv8"]:
        # TODO: fix update functionality for it in version_utils
        msg = f"update is disabled for tier-2 support {architecture}"
        logging.warning(msg)
        update = False
    else:
        update = True

    release_str = f"{version}-{system}-{architecture}"
    if do_release_check:
        rst = is_version_released(version, system, architecture,
                                  update=update)
        if not rst:
            msg = f"failed to find Julia release for {release_str}."
            logging.info(msg)
            return False

    logging.info(f"download Julia release for {release_str}")
    registry = SourceRegistry(upstream=upstream)
    url = registry.query_download_url(version, system, architecture,
                                      max_try=max_try)
    if not url:
        msg = f"failed to find available upstream for {release_str}"
        logging.warning(msg)
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
        logging.info(f"{outname} already exists, skip downloading")
        return outpath

    package_path = _download(url, outpath)

    if system in ["windows", "macos"]:
        # macOS and Windows releases are codesigned with certificates
        # that are verified by the operating system during installation
        return package_path
    elif system in ["linux", "freebsd"]:
        # need additional verification using GPG
        if not package_path:
            return package_path

        # a mirror should provides both *.tar.gz and *.tar.gz.asc
        gpg_signature_path = _download(url+".asc", outpath+".asc")
        if not gpg_signature_path:
            msg = f"failed to download GPG signature for {release_str}"
            logging.warning(msg)
            logging.info(f"remove untrusted/broken file")
            os.remove(package_path)
            return False

        if not verify_gpg(package_path, gpg_signature_path):
            logging.warning(f"failed to verify {release_str} downloads")
            msg = f"remove untrusted/broken files"
            logging.info(msg)
            os.remove(package_path)
            os.remove(gpg_signature_path)
            return False

        # GPG-verified julia release path
        logging.info(f"success to verify {release_str}")
        return package_path
    else:
        raise ValueError(f"unsupported system {sys}")
