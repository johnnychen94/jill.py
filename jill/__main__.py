from .download import download_package
from .install import install_julia
from .mirror import mirror
from .version_utils import update_releases
from .source import show_upstream
import fire
import logging
import os


def main():
    logging.basicConfig(filename=os.devnull,
                        level=logging.DEBUG)

    logging.basicConfig(level=logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    format = logging.Formatter('%(message)s')
    ch.setFormatter(format)
    logging.getLogger('').addHandler(ch)

    fire.Fire({
        'download': download_package,
        'install': install_julia,
        'mirror': mirror,
        'update': update_releases,
        'upstream': show_upstream
    }, name="jill")


if __name__ == "__main__":
    main()
