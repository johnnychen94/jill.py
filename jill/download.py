from .source import query_download_url_list
from .sys_utils import current_system, current_architecture

import requests
import wget
import os
import shutil
import tempfile
import logging

from urllib.parse import urlparse
from itertools import chain, repeat

from typing import Optional

from urllib.error import URLError
from requests.exceptions import RequestException


def _download_package(url: str, out: str):
    # always do overwrite
    outpath = os.path.abspath(out)
    outdir, outname = os.path.split(outpath)

    with tempfile.TemporaryDirectory() as temp_outdir:
        temp_outpath = os.path.join(temp_outdir, outname)
        try:
            print(f"downloading source: {url}")
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


def download_package(version, system=None, architecture=None,
                     outdir=None, overwrite=False, max_try=3):
    """
    download julia release from nearest servers.
    """
    system = system if system else current_system()
    architecture = architecture if architecture else current_architecture()
    print(f"download Julia release: {version}-{system}-{architecture}")

    url_list = query_download_url_list(version, system, architecture)

    url_list = chain.from_iterable(repeat(url_list, max_try))
    for url in url_list:
        outdir = outdir if outdir else '.'
        outdir = os.path.abspath(outdir)
        outname = os.path.split(urlparse(url).path)[1]
        outpath = os.path.join(outdir, outname)

        if os.path.isfile(outpath) and not overwrite:
            logging.info(f"{outname} already exists, skip downloading")
            return outpath

        try:
            logging.debug(f"try {url}")
            r = requests.head(url, timeout=10)
        except RequestException as e:
            logging.debug(f"failed: {str(e)}")
            continue
        if r.status_code == 404:
            logging.debug(f"failed: 404 error")
            continue
        rst = _download_package(url, outpath)
        if rst:
            return rst

    logging.warning(f"failed to find available upstream")
    return False
