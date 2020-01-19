from .download import download_package
from .install import install_julia
import fire
import logging


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(message)s')

    fire.Fire({
        'download': download_package,
        'install': install_julia,
    }, name="jill")


if __name__ == "__main__":
    main()
