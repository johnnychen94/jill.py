from .utils.defaults import default_path_template
from .utils.defaults import default_filename_template
from .utils.defaults import default_latest_filename_template
from .utils import generate_info
from .utils import read_releases
from .utils import current_system
from .download import download_package

from string import Template
from itertools import product

import semantic_version

import json
import os
import logging
import time


class MirrorConfig:
    def __init__(self, configfile, outdir, upstream=None):
        if current_system() == "windows":
            # Windows users (e.g., me) sometimes confuse the use of \\ and \
            outdir = outdir.replace("\\\\", "\\")
        self.configfile = os.path.abspath(os.path.expanduser(configfile))
        self.outdir = outdir
        self.upstream = upstream

    @property
    def config(self):
        if not os.path.isfile(self.configfile):
            return {}
        with open(self.configfile, 'r') as f:
            return json.load(f)

    @property
    def require_latest(self) -> bool:
        """True to mirror nightly build as well"""
        require_latest = self.config.get("require_latest", True)
        if isinstance(require_latest, bool):
            return require_latest
        if require_latest in ["False", "false"]:
            require_latest = False
        elif require_latest in ["True", "true"]:
            require_latest = True
        else:
            raise(ValueError(
                f"Unrecognized require_latest value: {require_latest}"))
        return require_latest

    @property
    def stable_only(self) -> bool:
        """True to not mirror alpha/beta/rc releases"""
        stable_only = self.config.get("stable_only", False)
        if isinstance(stable_only, bool):
            return stable_only
        if stable_only in ["False", "false"]:
            stable_only = False
        elif stable_only in ["True", "true"]:
            stable_only = True
        else:
            raise(ValueError(f"Unrecognized stable_only value: {stable_only}"))
        return stable_only

    @property
    def overwrite(self) -> bool:
        """
        True to overwrite existing stable releases as well.
        Nightly builds will be overwrite always regardless of this setting.
        """
        overwrite = self.config.get("overwrite", False)
        if isinstance(overwrite, bool):
            return overwrite
        if overwrite in ["False", "false"]:
            overwrite = False
        elif overwrite in ["True", "true"]:
            overwrite = True
        else:
            raise(ValueError(f"Unrecognized overwrite value: {overwrite}"))
        return overwrite

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
                                read_releases(stable_only=True, upstream=self.upstream))))
        # not using our extended Version
        versions.sort(key=lambda ver: semantic_version.Version(ver))
        if self.require_latest:
            versions.append("latest")
        return versions

    @property
    def system(self):
        return set(map(lambda x: x[1], read_releases(upstream=self.upstream)))

    @property
    def architecture(self):
        return set(map(lambda x: x[2], read_releases(upstream=self.upstream)))

    @property
    def releases(self):
        return read_releases(stable_only=self.stable_only, upstream=self.upstream)

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
    def __init__(self,  config, **kwargs):
        if not isinstance(config, MirrorConfig):
            config = MirrorConfig(config, **kwargs)
        self.config = config

    def pull_releases(self):
        for item in self.config.releases:
            filepath = self.config.get_outpath(*item)
            outpath = os.path.join(self.config.outdir, filepath)
            outdir, filename = os.path.split(outpath)

            logging.info(f"start to pull {filepath}")
            overwrite = self.config.overwrite
            download_package(*item,
                             outdir=outdir,
                             upstream=self.config.upstream,
                             overwrite=overwrite)
        if self.config.require_latest:
            for (system, arch) in product(self.config.system, self.config.architecture):
                item = "latest", system, arch
                filepath = self.config.get_outpath(*item)
                outpath = os.path.join(self.config.outdir, filepath)
                outdir, filename = os.path.split(outpath)

                logging.info(f"start to pull {filepath}")
                download_package(*item,
                                 outdir=outdir,
                                 upstream=self.config.upstream,
                                 overwrite=True)


def mirror(outdir="julia_pkg", *,
           period=0,
           upstream=None,
           logfile="mirror.log",
           config="mirror.json"):
    """
    Download/sync all Julia releases

    1. checks if there're new julia releases
    2. downloads all releases Julia releases into `outdir` (default `./julia_pkg`)
    3. (Optional): with flag `--period PERIOD`, it will repeat step 1 and 2 every `PERIOD` seconds

    If you want to modify the default mirror configuration, then provide a `mirror.json` file and
    pass the path to `config`. By default it's at the current directory.
    Arguments:
      outdir: default 'julia_pkg'.
      period: the time between two sync operation. 0(default) to sync once.
      upstream:
        manually choose a download upstream. For example, set it to "Official"
        if you want to download from JuliaComputing's s3 buckets.
      config:
        path to mirror config file
      logfile:
        path to mirror log file
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    period = int(period)
    upstream = None if upstream == "None" else upstream

    logger = logging.getLogger('')
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # TODO: filter out urllib3 debug logs

    m = Mirror(MirrorConfig(config, outdir=outdir, upstream=upstream))
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
