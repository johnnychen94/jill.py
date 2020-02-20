"""
tools to detect current system and architecture so that things work with tools
in the `filters` module
"""
import platform
import os


def current_system():
    rst = platform.system()
    if rst.lower() == "linux":
        return "linux"
    elif rst.lower() == "darwin":
        return "macos"
    elif rst.lower() == "freebsd":
        return "freebsd"
    elif rst.lower() == "windows":
        return "windows"
    else:
        raise ValueError(f"Unsupported system {rst}")


def current_architecture():
    arch = platform.machine()
    if arch.lower() == "aarch64":
        return "ARMv8"
    elif arch.lower() == "armv7l":
        return "ARMv7"
    elif arch.lower() == "i386":
        return "i686"
    elif arch.lower() == "amd64":
        return "x86_64"
    else:
        return arch


def show_verbose():
    if "GITHUB_ACTIONS" in os.environ:
        return True

    return os.environ.get("DEBUG", False)
