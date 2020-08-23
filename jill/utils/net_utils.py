from .sys_utils import show_verbose

from urllib.parse import urlparse
from ipaddress import ip_address

from requests_futures.sessions import FuturesSession
import socket
import requests
import time
import logging

from requests.exceptions import RequestException

from typing import Optional


def query_external_ip(cache=[], timeout=5):
    if cache:
        assert len(cache) == 1
        return cache[0]

    # try to use external ip address, if it fails, use the local ip address
    # failures could be due to several reasons, e.g., enterprise gateway
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        # store external ip because the query takes time
        cache.append(ip)
        return ip
    except RequestException:
        return socket.gethostbyname(socket.gethostname())


def query_ip(url: Optional[str] = None):
    if url:
        rst = urlparse(url)
        hostname = rst.netloc if rst.netloc else url
        if len(hostname) == 0:
            raise ValueError(f"invalid url {url}")
        try:
            ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            return "0.0.0.0"
    else:
        ip = query_external_ip()

    try:
        ip_address(ip)
    except ValueError:
        ip = '0.0.0.0'
    return ip


def port_response_time(host, port, timeout=2):
    """
    return the network latency to host:port, if the latency exceeds
    timeout then return timeout.

    If host is '0.0.0.0' then directly return a number larger than timeout.
    """
    if host == '0.0.0.0':
        return 10*timeout

    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    roundtrip = time.time() - start
    return min(roundtrip, timeout)


def first_response(url_lists, timeout):
    """
    send HEAD request to each url, return the first url that responses and skip drop all other urls.
    """
    def _query(url):
        if show_verbose():
            print(f"send HEAD request to {url}")
        return session.head(url, timeout=timeout, allow_redirects=True)

    if show_verbose():
        print(f"HEAD request timeout: {timeout}")

    with FuturesSession(max_workers=5) as session:
        futures = [_query(url) for url in url_lists]

        while True:
            time.sleep(0.1)

            status = [x.running() for x in futures]
            for future in futures:
                try:
                    if future.done() and future.result().status_code == 200:
                        return future.result().url
                except RequestException:
                    continue

            if not any(status):
                return None
