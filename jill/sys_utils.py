import sys
import platform


def current_system():
    if sys.platform == "linux" or sys.platform == "linux2":
        return "linux"
    elif sys.platform == "darwin":
        return "macos"
    elif sys.platform == "win32" or sys.platform == "win64":
        return "windows"


def current_architecture():
    return platform.machine()
