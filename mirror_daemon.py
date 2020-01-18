from jill import Mirror, MirrorConfig

import fire
import time
import logging

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def main(root: str = "julia_pkg",
         config="mirror.json",
         logfile: str = "mirror.log",
         period: int = 0,
         overwrite: bool = False):
    logging.basicConfig(filename=logfile,
                        level=logging.DEBUG,
                        format=log_format,
                        datefmt='%m-%d %H:%M')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

    m = Mirror(root, config, overwrite=overwrite)
    m.config.logging()
    while True:
        logging.info("START: pull Julia releases")
        m.pull_releases()
        logging.info("END: pulling Julia releases")

        if period == 0:
            return True
        else:
            time.sleep(period)

        # refresh configuration at each re-pull
        logging.info("reload configure file")
        m.config = MirrorConfig(config)
        m.config.logging()


if __name__ == '__main__':
    fire.Fire(main)
