from urllib.parse import urlparse
from ipaddress import ip_address

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


def is_url_available(url, timeout) -> bool:
    try:
        logging.debug(f"try {url}")
        r = requests.head(url, timeout=timeout)
    except RequestException as e:
        logging.debug(f"failed: {str(e)}")
        return False

    if r.status_code//100 == 4 or r.status_code//100 == 5:
        logging.debug(f"failed: {r.status_code} error")
        return False
    elif r.status_code == 301 or r.status_code == 302:
        # redirect
        new_url = r.headers['Location']
        return is_url_available(new_url, timeout)
    else:
        return True
