"""
tools to detect current system and architecture so that things work with tools
in the `filters` module
"""
import subprocess
import os
import platform
import warnings


def current_system():
    rst = platform.system()
    if rst.lower() == "linux":
        return "linux"
    elif rst.lower() == "darwin":
        return "mac"
    elif rst.lower() == "freebsd":
        return "freebsd"
    elif rst.lower() == "windows":
        return "winnt"
    else:
        raise ValueError(f"Unsupported system {rst}")


def current_architecture():
    arch = platform.machine()
    if arch.lower() == "aarch64":
        return "aarch64"
    elif arch.lower() == "armv7l":
        return "armv7l"
    elif arch.lower() == "i386":
        return "i686"
    elif arch.lower() == "amd64":
        return "x86_64"
    else:
        return arch


def current_libc():
    """
        current_libc()

    Detect which libc is used and return either "glibc" or "musl"
    """
    sys = current_system()
    if sys in ["linux", "freebsd"]:
        libc, _ = platform.libc_ver()
        if not libc:
            # in case glibc is not detected, we manually check the result of `ldd --version`
            # Reference:
            # https://unix.stackexchange.com/questions/120380/what-c-library-version-does-my-system-use
            ldd_call = subprocess.run(
                ["ldd", "--version"], capture_output=True)
            # musl `ldd --version` exits with 1
            version_string = ldd_call.stdout if ldd_call.returncode == 0 else ldd_call.stderr
            version_string = version_string.decode(
                "utf-8").splitlines()[0].lower()
            if "musl" in version_string:
                libc = "musl"
            elif "glibc" in version_string:
                libc = "glibc"
            else:
                warnings.warn(
                    f"failed to read libc version from {version_string}, use glibc as fallback")
                libc = "glibc"
        return libc
    else:
        raise ValueError(f"Unsupported system {sys}")


def show_verbose():
    if "GITHUB_ACTIONS" in os.environ:
        return True

    return os.environ.get("DEBUG", False)
