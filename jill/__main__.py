from .download import download_package
import fire

import logging
import sys
import platform


def current_system():
    if sys.platform == "linux" or sys.platform == "linux2":
        return "linux"
    elif sys.platform == "darwin":
        return "macos"
    elif sys.platform == "win32" or sys.platform == "win64":
        return "windows"


def _main(version, system=None, architecture=None, download_only=False):
    system = system if system else current_system()
    architecture = architecture if architecture else platform.machine()

    print(f"download Julia release: {version}-{system}-{architecture}")
    rst = download_package(version, system, architecture)


def main():
    fire.Fire(_main, name="jill")


if __name__ == "__main__":
    main()
