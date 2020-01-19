from .defaults import default_path_template
from .defaults import default_filename_template
from .defaults import default_latest_filename_template
from .defaults import MIRROR_CONFIGFILE
from .download import download_package
from .filters import generate_info, is_valid_release
from .filters import VALID_SYSTEM, VALID_ARCHITECTURE
from .version_utils import update_releases

from string import Template
from itertools import product

import json
import os
import logging
import time

from typing import List


class MirrorConfig:
    def __init__(self, configfile, outdir):
        configfile_list = [os.path.abspath(os.path.expanduser(configfile)),
                           MIRROR_CONFIGFILE]
        self.configfile = next(filter(os.path.isfile, configfile_list))
        self.outdir = outdir

    @property
    def config(self):
        if not os.path.isfile(self.configfile):
            return {}
        with open(self.configfile, 'r') as f:
            return json.load(f)

    @property
    def path_template(self):
        return Template(self.config.get("path", default_path_template))

    @property
    def filename_template(self):
        return Template(self.config.get("filename", default_filename_template))

    @property
    def latest_filename_template(self):
        return Template(self.config.get("latest_filename",
                                        default_latest_filename_template))

    @property
    def overwrite(self):
        s_overwrite = self.config.get("overwrite", "false")
        return True if s_overwrite.lower() == "true" else False

    @property
    def version(self):
        releases = self.config.get("releases", {})
        if not releases:
            logging.warning(
                "no Julia versions found, nothing will be downloaded")
        return releases.get("version", [])

    @property
    def system(self):
        releases = self.config.get("releases", {})
        return releases.get("system", VALID_SYSTEM)

    @property
    def architecture(self):
        releases = self.config.get("releases", {})
        return releases.get("architecture", VALID_ARCHITECTURE)

    @property
    def releases(self):
        items = product(self.version, self.system, self.architecture)
        return list(filter(lambda item: is_valid_release(*item), items))

    def logging(self):
        logging.info(f"mirror configuration:")
        logging.info(f"    - configfile: {self.configfile}")
        logging.info(f"    - outdir: {self.outdir}")
        logging.info(f"    - path: {self.path_template.template}")
        logging.info(f"    - filename: {self.filename_template.template}")
        logging.info(f"    - versions: {', '.join(self.version)}")
        logging.info(f"    - systems: {', '.join(self.system)}")
        logging.info(f"    - architectures: {', '.join(self.architecture)}")
        logging.info(f"    - overwrite: {self.overwrite}")

    def get_outpath(self, plain_version, system, architecture):
        configs = generate_info(plain_version, system, architecture)
        if plain_version in ["latest"]:
            t_file = self.latest_filename_template
        else:
            t_file = self.filename_template
        configs["filename"] = t_file.substitute(**configs)
        return self.path_template.substitute(**configs)


class Mirror:
    def __init__(self,  config):
        if not isinstance(config, MirrorConfig):
            config = MirrorConfig(config)
        self.config = config
        self.failed_releases = self.config.releases

    def pull_releases(self):
        failed_releases = self.failed_releases.copy()
        for item in self.failed_releases:
            filepath = self.config.get_outpath(*item)
            outpath = os.path.join(self.config.outdir, filepath)
            outdir, filename = os.path.split(outpath)

            logging.info(f"start to pull {filepath}")
            overwrite = True if item[0] == "latest" else self.config.overwrite
            rst = download_package(*item, outdir, overwrite)
            assert os.path.exists(outpath)
            if rst:
                assert item in self.failed_releases
                failed_releases.remove(item)
        self.failed_releases = failed_releases


def mirror(period=0,
           outdir="julia_pkg",
           logfile="mirror.log",
           config="mirror.json"):
    """
    periodly download/sync all Julia releases
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logger = logging.getLogger('')
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # TODO: filter out urllib3 debug logs

    config = MirrorConfig(config, outdir=outdir)
    m = Mirror(config)
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
        m.config = MirrorConfig(config, outdir=outdir)
        m.config.logging()
        logging.info("check if there're new releases")
        update_releases(system="all", architecture="all")
