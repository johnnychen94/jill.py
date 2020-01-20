from .defaults import fb_release_url_template
from .defaults import fb_nightly_url_template
from .defaults import default_filename_template
from .defaults import default_latest_filename_template
from .defaults import default_scheme_ports
from .defaults import SOURCE_CONFIGFILE

from .net_utils import query_ip, port_response_time
from .filters import generate_info

from itertools import chain, repeat
from urllib.parse import urlparse
from string import Template

import requests
import json
import os
import logging

from typing import Optional

from requests.exceptions import RequestException


class ReleaseSource:
    def __init__(self,
                 name: str,
                 url: str,
                 filename: str = default_filename_template,
                 latest_filename: str = default_latest_filename_template):
        # TODO: merge filename and lastest_filename to a list
        self.name = name

        self.url_template = Template(url)
        self.filename_template = Template(filename)
        self.latest_filename_template = Template(latest_filename)

    @property
    def url(self):
        return self.url_template.template

    @property
    def filename(self):
        return self.filename_template.template

    @property
    def netloc(self):
        return urlparse(self.url).netloc

    @property
    def port(self):
        return default_scheme_ports[urlparse(self.url).scheme]

    def __repr__(self):
        return f"ReleaseSource({self.name})"

    def get_url(self, plain_version, system, architecture):
        configs = generate_info(plain_version, system, architecture)
        if plain_version in ["latest"]:
            t_file = self.latest_filename_template
        else:
            t_file = self.filename_template
        configs["filename"] = t_file.substitute(**configs)
        return self.url_template.substitute(**configs)


def read_upstream(cfg_file=SOURCE_CONFIGFILE):
    temp_file_list = [os.path.split(cfg_file)[1], cfg_file]
    file_list = list(filter(os.path.isfile, temp_file_list))
    if not len(file_list):
        return {}
    with open(file_list[0], 'r') as f:
        return json.load(f).get("upstream", {})


def initialize_upstream_sources(timeout=2, sources=[]):
    # TODO: save initialized sources into a config file as "permanent" cache
    if len(sources):
        return sources

    logging.info(f"initialize upstream sources")
    fallback_server_list = [
        ReleaseSource("Julia Computing -- stable releases",
                      url=fb_release_url_template),
        ReleaseSource("Julia Computing -- nightly releases",
                      url=fb_nightly_url_template)
    ]
    config_server_list = [ReleaseSource(**item) for item in read_upstream()]
    origin_list = []
    origin_list.extend(fallback_server_list)
    origin_list.extend(config_server_list)

    # sort upstreams according to responsing time
    # TODO: stop checking new servers if there're already max_sources
    response_times = [port_response_time(query_ip(x.url), x.port, timeout)
                      for x in origin_list]
    for idx in range(len(fallback_server_list)):
        # don't filter out JuliaComputing servers even if there're unavailable
        if response_times[idx] > timeout:
            response_times[idx] = timeout
    src_list = list(filter(lambda src: src[1] <= timeout,
                           zip(origin_list, response_times)))
    src_list.sort(key=lambda x: x[1])
    sources.extend([x[0] for x in src_list])

    logging.info(f"found {len(sources)} available resources:")
    for src in sources:
        logging.info("    - " + str(src))

    return sources


def query_download_url_list(version: str,
                            system: str,
                            architecture: str):
    """
    return a list of potential download urls. There's no guarantee that
    all urls are valid.
    """
    sources = initialize_upstream_sources()
    return [s.get_url(version, system, architecture) for s in sources]


def is_url_available(url, timeout):
    try:
        logging.debug(f"try {url}")
        r = requests.head(url, timeout=timeout)
    except RequestException as e:
        logging.debug(f"failed: {str(e)}")
        return False

    if r.status_code//100 == 4:
        logging.debug(f"failed: {r.status_code} error")
        return False
    elif r.status_code == 301 or r.status_code == 302:
        # redirect
        new_url = r.headers['Location']
        return is_url_available(new_url, timeout)
    else:
        return True


def query_download_url(version, system, arch, max_try=3, timeout=10):
    """
    return a valid download url to nearest mirror server. If there isn't
    such version then return None.
    """
    url_list = query_download_url_list(version, system, arch)

    url_list = chain.from_iterable(repeat(url_list, max_try))
    for url in url_list:
        if is_url_available(url, timeout):
            return url
    return None
