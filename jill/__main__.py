from .download import download_package
from .install import install_julia
from .utils import show_upstream
import fire
import logging
import os


def main():
    logging.basicConfig(filename=os.devnull,
                        level=logging.DEBUG)

    fire.Fire({
        'download': download_package,
        'install': install_julia,
        'upstream': show_upstream
    }, name="jill")


if __name__ == "__main__":
    main()
