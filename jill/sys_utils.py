import platform


def current_system():
    rst = platform.system()
    if rst == "Linux":
        return "linux"
    elif rst == "Darwin":
        return "macos"
    elif rst == "FreeBSD":
        return "freebsd"
    elif rst == "Windows":
        return "windows"
    else:
        raise ValueError(f"Unsupported system {rst}")


def current_architecture():
    arch = platform.machine()
    if arch == "aarch64":
        return "ARMv8"
    elif arch == "armv7l":
        return "ARMv7"
    else:
        return arch
