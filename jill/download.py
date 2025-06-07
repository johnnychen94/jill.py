from .utils import SourceRegistry, verify_upstream
from .utils import latest_version
from .utils import is_version_released
from .utils import is_full_version
from .utils import current_system, current_architecture, current_libc
from .utils import verify_gpg
from .utils import color
from .utils.filters import canonicalize_sys, canonicalize_arch
from .utils.net_utils import download

import re
import os
import shutil
import ssl
import tempfile
import logging
from urllib.parse import urlparse

from urllib.error import URLError


class SSLContext:
    # https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error
    def __init__(self, create_context=None):
        if create_context:
            self.prev_create_context = ssl._create_default_https_context
            self.create_context = create_context
        else:
            self.create_context = None

    def __enter__(self):
        if self.create_context:
            ssl._create_default_https_context = self.create_context

    def __exit__(self, type, value, tb):
        if self.create_context:
            ssl._create_default_https_context = self.prev_create_context


def _download(url: str, out: str, *, bypass_ssl: bool = False):
    # always do overwrite
    outpath = os.path.abspath(out)
    outdir, outname = os.path.split(outpath)

    with tempfile.TemporaryDirectory() as temp_outdir:
        temp_outpath = os.path.join(temp_outdir, outname)
        try:
            msg = f"downloading from {url}"
            logging.info(msg)
            print(msg)
            if bypass_ssl:
                print(f"{color.YELLOW}skip SSL certificate validation{color.END}")
            download(url, temp_outpath, bypass_ssl=bypass_ssl)
            print()  # for format usage
            msg = f"finished downloading {outname}"
            print(f"{color.GREEN}{msg}{color.END}")
        except (URLError, ConnectionError, Exception) as e:
            msg = f"failed to download {outname}: {str(e)}"
            logging.info(msg)
            print(f"{color.RED}{msg}{color.END}")
            return False

        if not os.path.isdir(outdir):
            os.makedirs(outdir, exist_ok=True)
        shutil.move(temp_outpath, outpath)

    return outpath


def download_package(
    version=None,
    sys=None,
    arch=None,
    upstream=None,
    unstable=False,
    outdir=None,
    overwrite=False,
    bypass_ssl=False,
):
    """Download Julia release from nearest servers.

    Args:
        version: Julia version to download
        sys: Target system (linux, musl, macos, freebsd, windows)
        arch: Target architecture (i686, x86_64, ARMv7, ARMv8)
        upstream: Custom upstream URL
        unstable: Allow unstable versions
        outdir: Output directory
        overwrite: Overwrite existing files
        bypass_ssl: Skip SSL verification
    """
    version = str(version) if (version or str(version) == "0") else ""
    version = "latest" if version == "nightly" else version
    version = "" if version == "stable" else version
    upstream = upstream if upstream else os.environ.get("JILL_UPSTREAM", None)

    system = sys if canonicalize_sys(sys) else current_system()
    if system == "linux" and current_system() == "linux" and current_libc() == "musl":
        # currently Julia tags musl as a system, e.g.,
        # https://julialang-s3.julialang.org/bin/musl/x64/1.5/julia-1.5.1-musl-x86_64.tar.gz
        system = "musl"
    architecture = arch if canonicalize_arch(arch) else current_architecture()

    match_build = re.match("(.*)\+(\w+)$", version)
    if match_build:
        # These files are only available in OfficialNightlies upstream and we don't need to spend
        # time on querying other upstreams.
        upstream = "OfficialNightlies"
        build = match_build.group(2)
        print(
            f"Detected julia build commit {build}, downloading from upstream {upstream}"
        )  # nopep8

    # allow downloading unregistered releases, e.g., 1.4.0-rc1
    do_release_check = not (is_full_version(version) or match_build)

    if upstream:
        verify_upstream(upstream)
    wrong_args = False
    try:
        version = latest_version(
            version, system, architecture, upstream=upstream, stable_only=not unstable
        )
    except ValueError:
        # hide the nested error stack :P
        wrong_args = True
    if wrong_args:
        msg = "something wrong for the platform argument you passed:\n"
        msg += f"  - version(>= 0.6.0): {version}\n"
        msg += f"  - system: {system}\n"
        msg += f"  - archtecture: {architecture}\n"
        msg += "example: `jill download 1 linux x86_64`"
        raise (ValueError(msg))

    release_str = f"{version}-{system}-{architecture}"
    if do_release_check:
        rst = is_version_released(version, system, architecture, upstream=upstream)
        if not rst:
            msg = f"failed to find {release_str} in available upstream. Please try it later."
            logging.info(msg)
            print(f"{color.RED}{msg}{color.END}")
            return False

    msg = f"downloading Julia release for {release_str}"
    logging.info(msg)
    print(msg)

    if version in ["latest", "nightly"] or match_build:
        # It usually takes longer to query from nightlies bucket so please be patient
        timeout = 30
        print(f"Set timeout {timeout} seconds")
    else:
        timeout = 5

    def query_url(upstream, timeout=timeout):
        registry = SourceRegistry(upstream=upstream)
        url = registry.query_download_url(
            version, system, architecture, timeout=timeout
        )
        if url:
            return url
        # if fails to find an valid url in given upstream, falls back to "Official"
        if upstream in ["Official", "OfficialNightlies"] or upstream is None:
            # if "Official" is already tried, then there's no need to retry
            return None
        else:
            msg = f"failed to find {release_str} in upstream {upstream}. Fallback to upstream Official."
            logging.warning(msg)
            print(f"{color.RED}{msg}{color.END}")
            return query_url("Official")  # fallback to Official

    url = query_url(upstream)
    if not url:
        msg = (
            f"failed to find {release_str} in available upstreams. Please try it later."
        )
        logging.error(msg)
        print(f"{color.RED}{msg}{color.END}")
        return None

    outdir = outdir if outdir else "."
    outdir = os.path.abspath(outdir)
    if current_system() == "winnt":
        outdir = outdir.replace("\\\\", "\\")

    # Convert URL to string before parsing
    url_str = str(url)
    outname = os.path.basename(urlparse(url_str).path)
    outpath = os.path.join(outdir, outname)

    skip_download = False
    if system in ["linux", "freebsd"]:
        if (
            os.path.isfile(outpath)
            and os.path.isfile(outpath + ".asc")
            and not overwrite
        ):
            skip_download = True
    else:
        if os.path.isfile(outpath) and not overwrite:
            skip_download = True
    if skip_download:
        msg = f"{outname} already exists, skip downloading"
        logging.info(msg)
        print(f"{color.GREEN}{msg}{color.END}")
        return outpath

    package_path = _download(url, outpath, bypass_ssl=bypass_ssl)

    if system in ["winnt", "mac"]:
        # macOS and Windows releases are codesigned with certificates
        # that are verified by the operating system during installation
        return package_path
    elif system in ["linux", "freebsd", "musl"]:
        # need additional verification using GPG
        if not package_path:
            return package_path

        # a mirror should provides both *.tar.gz and *.tar.gz.asc
        gpg_signature_path = _download(
            url + ".asc", outpath + ".asc", bypass_ssl=bypass_ssl
        )
        if not gpg_signature_path:
            msg = f"failed to download GPG signature for {release_str}\n"
            msg += "remove untrusted/broken file"
            logging.info(msg)
            print(f"{color.RED}{msg}{color.END}")
            os.remove(package_path)
            return False

        if not verify_gpg(package_path, gpg_signature_path):
            msg = f"failed to verify {release_str} downloads\n"
            msg += "remove untrusted/broken files"
            logging.info(msg)
            print(f"{color.RED}{msg}{color.END}")
            os.remove(package_path)
            os.remove(gpg_signature_path)
            return False

        # GPG-verified julia release path
        msg = f"verifying {release_str} succeed"
        logging.info(msg)
        print(f"{color.GREEN}{msg}{color.END}")
        return package_path
    else:
        os.remove(package_path)
        raise ValueError(f"unsupported system {sys}")
