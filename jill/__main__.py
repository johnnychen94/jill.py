from .download import download_package
from .install import install_julia
import fire

import logging


def main():
    fire.Fire({
        'download': download_package,
        'install': install_julia,
    }, name="jill")


if __name__ == "__main__":
    main()
