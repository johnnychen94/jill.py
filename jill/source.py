from .defaults import fb_release_url_template
from .defaults import fb_nightly_url_template
from .defaults import default_filename_template
from .defaults import default_latest_filename_template
from .defaults import default_scheme_ports
from .defaults import SOURCE_CONFIGFILE

from .net_utils import query_ip, port_response_time
from .filters import generate_info

from urllib.parse import urlparse
from string import Template

import json
import os
import logging

from typing import Optional


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

    @property
    def is_available(self):
        return is_port_open(self.netloc, self.port)

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


def read_upstream():
    """
    read configure file from:
    1. `./sources.json`
    2. `~/.config/jill/sources.json`
    """
    cfg_file = os.path.abspath(os.path.expanduser(SOURCE_CONFIGFILE))
    temp_file_list = [os.path.split(cfg_file)[1], cfg_file]
    file_list = list(filter(os.path.isfile, temp_file_list))
    if not len(file_list):
        return {}
    with open(file_list[0], 'r') as f:
        return json.load(f).get("upstream", {})


def get_download_sources(max_sources=10, timeout=2, sources=[]):
    assert max_sources >= 1

    # TODO: save initialized sources into a config file as "permanent" cache
    if len(sources):
        return sources

    logging.info(f"initialize upstream sources")
    origin_list = [ReleaseSource(**item) for item in read_upstream()]

    # sort upstreams according to responsing time
    # TODO: stop checking new servers if there're already max_sources
    response_times = [port_response_time(query_ip(x.url), x.port, timeout)
                      for x in origin_list]
    temp_list = list(zip(origin_list, response_times))
    temp_list.sort(key=lambda x: x[1])
    temp_list = list(filter(lambda src: src[1] < timeout, temp_list))
    src_list = [x[0] for x in temp_list[0:max_sources]]

    # don't filter out fallback, just push them to the end
    sources.extend(src_list)
    sources.append(ReleaseSource("Julia Computing -- stable releases",
                                 url=fb_release_url_template))
    sources.append(ReleaseSource("Julia Computing -- nightly releases",
                                 url=fb_nightly_url_template))

    logging.info(f"found {len(sources)} available resources:")
    for src in sources:
        logging.info("    - " + str(src))

    return sources


def query_download_url_list(version: str,
                            system: str,
                            architecture: str):
    sources = get_download_sources()
    return [s.get_url(version, system, architecture) for s in sources]
