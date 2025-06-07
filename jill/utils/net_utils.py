from .sys_utils import show_verbose

from urllib.parse import urlparse
from ipaddress import ip_address

import httpx
import socket
import time
from pathlib import Path

from typing import Optional


def query_external_ip(cache=[], timeout=5):
    if cache:
        assert len(cache) == 1
        return cache[0]

    # try to use external ip address, if it fails, use the local ip address
    # failures could be due to several reasons, e.g., enterprise gateway
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get("https://api.ipify.org")
            response.raise_for_status()
            ip = response.text
            # store external ip because the query takes time
            cache.append(ip)
            return ip
    except httpx.HTTPError:
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
        ip = "0.0.0.0"
    return ip


def port_response_time(host, port, timeout=2):
    """
    return the network latency to host:port, if the latency exceeds
    timeout then return timeout.

    If host is '0.0.0.0' then directly return a number larger than timeout.
    """
    if host == "0.0.0.0":
        return 10 * timeout

    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect_ex((host, port))  # We only care if it connects, not the result
    roundtrip = time.time() - start
    return min(roundtrip, timeout)


def first_response(url_lists, timeout):
    """
    send GET request to each url, return the first url that responses and skip drop all other urls.
    The connection is closed after receiving the first few bytes to optimize performance.
    """

    async def _query(url):
        if show_verbose():
            print(f"send GET request to {url}")
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            with client.stream("GET", url) as r:
                for chunk in r.iter_bytes():
                    if chunk:
                        return r
        return None

    if show_verbose():
        print(f"GET request timeout: {timeout}")

    # Use asyncio for concurrent requests
    import asyncio

    async def _async_query(url):
        try:
            response = await _query(url)
            if show_verbose():
                print(f"response {url} with status code {response.status_code}")
            if response.status_code == 200:
                return url
        except httpx.HTTPError as e:
            if show_verbose():
                print(f"HTTPError: {url} {e}")
            pass
        return None

    async def _main():
        tasks = []
        for url in url_lists:
            task = asyncio.create_task(_async_query(url))
            tasks.append(task)
            try:
                result = await task
                if result:
                    # Cancel all remaining tasks when we get a successful response
                    for t in tasks:
                        if not t.done():
                            t.cancel()
                    return result
            except asyncio.CancelledError:
                continue
        return None

    return asyncio.run(_main())


def download(url, outpath, *, bypass_ssl=False):
    """
    Download a file from `url` to `outpath` using httpx.
    Automatically follows redirects (including 301) to get the final file.
    """

    verify = not bypass_ssl
    with httpx.Client(verify=verify, follow_redirects=True) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            filename = Path(outpath).name

            with open(outpath, "wb") as f:
                for chunk in response.iter_bytes():
                    if chunk:
                        f.write(chunk)
                print(f"Downloaded {filename} successfully")
