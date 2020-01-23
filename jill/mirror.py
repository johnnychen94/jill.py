from .defaults import default_path_template
from .defaults import default_filename_template
from .defaults import default_latest_filename_template
from .download import download_package
from .filters import generate_info, is_valid_release
from .version_utils import update_releases
from .version_utils import read_releases

from string import Template
from itertools import product
from semantic_version import Version

import json
import os
import logging
import time

from typing import List


class MirrorConfig:
    def __init__(self, configfile, outdir):
        self.configfile = os.path.abspath(os.path.expanduser(configfile))
        self.outdir = outdir

    @property
    def config(self):
        if not os.path.isfile(self.configfile):
            return {}
        with open(self.configfile, 'r') as f:
            return json.load(f)

    @property
    def require_latest(self):
        """True to mirror nightly build as well"""
        return self.config.get("require_latest", True)

    @property
    def overwrite(self):
        """
        True to overwrite existing stable releases as well.
        Nightly builds will be overwrite always regardless of this setting.
        """
        return self.config.get("overwrite", False)

    @property
    def path_template(self):
        """path template to define the folder structure of releases"""
        return Template(self.config.get("path", default_path_template))

    @property
    def filename_template(self):
        """filename template for stable releases"""
        return Template(self.config.get("filename", default_filename_template))

    @property
    def latest_filename_template(self):
        """filename template for nightly builds"""
        return Template(self.config.get("latest_filename",
                                        default_latest_filename_template))

    @property
    def version(self):
        versions = list(set(map(lambda x: x[0],
                                read_releases(stable_only=True))))
        versions.sort(key=lambda ver: Version(ver))
        if self.require_latest:
            versions.append("latest")
        return versions

    @property
    def system(self):
        return set(map(lambda x: x[1], read_releases()))

    @property
    def architecture(self):
        return set(map(lambda x: x[2], read_releases()))

    @property
    def releases(self):
        stable_only = False if self.require_latest else True
        return read_releases(stable_only)

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
        logging.info(f"    - require_latest: {self.require_latest}")

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

    def pull_releases(self, *,
                      upstream=None):
        for item in self.config.releases:
            filepath = self.config.get_outpath(*item)
            outpath = os.path.join(self.config.outdir, filepath)
            outdir, filename = os.path.split(outpath)

            logging.info(f"start to pull {filepath}")
            overwrite = True if item[0] == "latest" else self.config.overwrite
            download_package(*item,
                             outdir=outdir,
                             upstream=upstream,
                             overwrite=overwrite)


def mirror(outdir="julia_pkg", *,
           period=0,
           upstream=None,
           logfile="mirror.log",
           config="mirror.json"):
    """
    periodly download/sync all Julia releases

    Arguments:
    outdir: default 'julia_pkg'.
    period: the time between two sync operation. 0(default) to sync once.
    upstream:
        manually choose a download upstream. For example, set it to "Official"
        if you want to download from JuliaComputing's s3 buckets.
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
        update_releases(system="all", architecture="all")

        logging.info("START: pull Julia releases")
        m.pull_releases(upstream=upstream)
        logging.info("END: pulling Julia releases")

        if period == 0:
            return True
        else:
            time.sleep(period)

        # refresh configuration at each re-pull
        logging.info("reload configure file")
        m.config = MirrorConfig(config, outdir=outdir)
        m.config.logging()
