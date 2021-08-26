from .download import download_package
from .install import install_julia
from .utils import show_upstream
from .mirror import mirror
from .list import list_julia
from .switch import switch_julia_target
import fire
import logging
import os


def main():
    logging.basicConfig(filename=os.devnull,
                        level=logging.DEBUG)

    fire.Fire({
        'download': download_package,
        'install': install_julia,
        'upstream': show_upstream,
        'mirror': mirror,
        'list': list_julia,
        'switch': switch_julia_target,
    }, name="jill")


if __name__ == "__main__":
    main()
