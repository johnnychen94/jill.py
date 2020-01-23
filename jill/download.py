from .source import SourceRegistry
from .version_utils import latest_version
from .version_utils import is_version_released
from .sys_utils import current_system, current_architecture

import wget
import os
import shutil
import tempfile
import logging

from urllib.parse import urlparse

from typing import Optional

from urllib.error import URLError


def _download_package(url: str, out: str):
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
                     update=False,
                     max_try=3):
    """
    download julia release from nearest servers

    Arguments:
      version: Option examples: 1, 1.2, 1.2.3, latest.
      By default it's the latest stable release. See also `jill update`
      sys: Options are: "linux", "macos", "freebsd", "windows"
      arch: Options are: "i686", "x86_64", "ARMv7", "ARMv8"
      upstream:
        manually choose a download upstream. For example, set it to "Official"
        if you want to download from JuliaComputing's s3 buckets.
      outdir: where release is downloaded to. By default it's current folder.
      overwrite: True to overwrite existing releases. By default it's False.
      update: add `--update` to update release info before downloading.
      max_try: try `max_try` times before returning a False.
    """
    version = str(version) if version else ''
    system = sys if sys else current_system()
    architecture = arch if arch else current_architecture()

    version = latest_version(version, system, architecture)
    release_str = f"{version}-{system}-{architecture}"
    if not is_version_released(version, system, architecture):
        if not update:
            msg = f"{release_str} seems not to be released yet."
            msg += " you can run 'jill update' first " + \
                   " or add an '--update' flag to current command."
            logging.info(msg)
            return False
        else:
            rst = is_version_released(version, system, architecture,
                                      update=True)
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
    outname = os.path.split(urlparse(url).path)[1]
    outpath = os.path.join(outdir, outname)

    if os.path.isfile(outpath) and not overwrite:
        logging.info(f"{outname} already exists, skip downloading")
        return outpath
    return _download_package(url, outpath)
