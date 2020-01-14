from urllib.parse import urlparse
import socket
import requests
import time
from ipaddress import ip_address

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
        hostname = urlparse(url).netloc
        assert len(hostname)
        ip = socket.gethostbyname(hostname)
    else:
        ip = query_external_ip()

    try:
        ip_address(ip)
    except ValueError:
        ip = '0.0.0.0'
    return ip


def port_response_time(host, port, timeout=2):
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    roundtrip = time.time() - start
    return roundtrip
