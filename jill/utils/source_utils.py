"""
This module provides tools to read information about upstream mirror, e.g.,
if it has a specific julia download.
"""
from .defaults import default_scheme_ports
from .defaults import SOURCE_CONFIGFILE
from .net_utils import query_ip
from .net_utils import port_response_time
from .net_utils import is_url_available
from .sys_utils import show_verbose
from .filters import generate_info
from .interactive_utils import color

from itertools import chain, repeat
from urllib.parse import urlparse
from string import Template

import requests
import json
import os

from typing import List

from requests.exceptions import RequestException


class ReleaseSource:
    def __init__(self,
                 name: str,
                 urls: List[str],
                 latest_urls: List[str],
                 timeout=2.0):
        # seperate stable and nightly versions because:
        #   * JuliaComputing stores them in two different s3 buckets
        #   * not all mirror servers need/want to serve nightly releases
        # store multiple urls because:
        #   * many mirrors have different multiple domains for different
        #     network choices, e.g., ipv4, ipv6, cernet, chinanet, rsync
        self.name = name
        self.url_templates = [Template(x) for x in urls]
        # TODO: make latest an optional config
        self.latest_url_templates = [Template(x) for x in latest_urls if x]
        self.timeout = timeout
        self._latencies = dict()  # type: ignore

    @property
    def urls(self):
        return [x.template for x in self.url_templates]

    @property
    def latest_urls(self):
        return [x.template for x in self.latest_url_templates]

    @property
    def hosts(self):
        return [urlparse(url).netloc for url in self.urls]

    @property
    def latest_hosts(self):
        return [urlparse(url).netloc for url in self.latest_urls]

    @property
    def latencies(self):
        # only check latency once and lazily
        if not self._latencies:
            url_list = self.urls.copy()
            url_list.extend(self.latest_urls)
            host_list = [urlparse(url).netloc for url in url_list]

            # hosts might point to the same ip address
            host_ip_records = {host: query_ip(host) for host in host_list}
            ip_port_records = {host_ip_records[urlparse(url).netloc]:
                               default_scheme_ports[urlparse(url).scheme]
                               for url in url_list}

            latency_records = dict()
            # TODO: use threads
            for ip, port in ip_port_records.items():
                latency_records[ip] = port_response_time(ip, port,
                                                         self.timeout)
            self._latencies = {host: latency_records[host_ip_records[host]]
                               for host in host_list}
        return self._latencies

    def __repr__(self):
        return f"ReleaseSource('{self.name}')"

    def get_url(self, plain_version, system, architecture):
        """
        return one potential downloading url with minal network latency for
        specific version, system and architecture. Special version name such
        as 'latest' are treated differently.
        """
        if plain_version == "latest":
            template_lists = self.latest_url_templates
        else:
            template_lists = self.url_templates
        configs = generate_info(plain_version, system, architecture)
        url_list = [t.substitute(**configs) for t in template_lists]
        url_list.sort(key=lambda url:
                      self.latencies[urlparse(url).netloc])
        return url_list[0] if url_list else ""


def read_registry():
    registry = dict()
    for cfg_file in reversed(SOURCE_CONFIGFILE):
        if not os.path.isfile(cfg_file):
            continue
        with open(cfg_file, 'r') as f:
            upstream_records = json.load(f).get("upstream", {})
            temp_registry = {k: ReleaseSource(**v)
                             for k, v in upstream_records.items()}
        registry.update(temp_registry)
    return registry


def latency_string(latency):
    latency *= 1000
    if latency <= 100:
        latency = f"{color.GREEN}{latency:.0f}{color.END}"
    elif latency <= 200:
        latency = f"{color.YELLOW}{latency:.0f}{color.END}"
    else:
        latency = f"{color.RED}{latency:.0f}{color.END}"
    return latency


class SourceRegistry:
    # share the same "full" registry across all instances
    class __SourceRegistry:
        def __init__(self, timeout):
            self.timeout = timeout
            self.registry = read_registry()

    __inner_registry = None

    def __init__(self, *, upstream=None, timeout=2):
        self.upstream = upstream
        if not self.__inner_registry:
            self.__inner_registry = self.__SourceRegistry(timeout)

    @property
    def registry(self):
        if self.upstream:
            # users limit themselves to only one download source
            if self.upstream in self.__inner_registry.registry:
                return {self.upstream:
                        self.__inner_registry.registry[self.upstream]}
            else:
                msg = "valid sources are:" + \
                    ', '.join(self.__inner_registry.registry.keys())
                raise ValueError(msg)
        return self.__inner_registry.registry

    @property
    def latencies(self):
        records = dict()
        for src in self.registry.values():
            records.update(src.latencies)
        return records

    def __len__(self):
        return len(self.registry)

    def info(self):
        msg = f"Found {len(self)} release sources:\n\n"
        for name, resource in self.registry.items():
            msg += f"- {color.BOLD}{name}{color.END}: {resource.name}\n"

            hosts = set(resource.hosts)
            latest_hosts = set(resource.latest_hosts)
            diff = latest_hosts - hosts
            for host in resource.hosts + list(diff):
                latency = latency_string(resource.latencies[host])
                msg += f"  * {host} ({latency} ms)\n"
        return msg

    def _get_urls(self, plain_version, system, architecture):
        """
        return a list of potential downloading urls for specific version,
        system and architecture. Special version name such as 'latest' are
        treated differently.
        """
        url_list = [src.get_url(plain_version, system, architecture)
                    for src in self.registry.values()]
        url_list = [url for url in url_list if url]
        url_list.sort(key=lambda url:
                      self.latencies[urlparse(url).netloc])
        return url_list

    def query_download_url(self,
                           version, system, arch, *,
                           max_try=3, timeout=10):
        """
        return a valid download url to nearest mirror server. If there isn't
        such version then return None.
        """
        url_list = self._get_urls(version, system, arch)

        url_list = chain.from_iterable(repeat(url_list, max_try))
        for url in url_list:
            if show_verbose():
                print(f"query {url}")
            if is_url_available(url, timeout):
                return url
        return None


def show_upstream():
    """print all registered upstream servers"""
    registry = SourceRegistry()
    print(registry.info())


def verify_upstream(registry_name):
    registry = SourceRegistry()
    if registry_name not in registry.registry:
        available_names = '"' + '", "'.join(registry.registry.keys()) + '"'
        raise(ValueError(
            f'registry "{registry_name}" not in {available_names}'))
