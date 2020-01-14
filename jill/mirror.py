from .defaults import default_path_template
from .defaults import default_filename_template
from .download import download_package
from .filters import generate_info, is_valid_release
from .filters import VALID_SYSTEM, VALID_ARCHITECTURE

from string import Template
from itertools import product

import json
import os
import logging

from typing import List


class MirrorConfig:
    def __init__(self, configfile):
        self.configfile = configfile

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
    def version(self):
        releases = self.config.get("releases", {})
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
        logging.info(f"    - versions: {self.version}")
        logging.info(f"    - systems: {self.system}")
        logging.info(f"    - architectures: {self.architecture}")

    def get_outpath(self, plain_version, system, architecture):
        configs = generate_info(plain_version, system, architecture)
        configs["filename"] = self.filename_template.substitute(**configs)
        return self.path_template.substitute(**configs)


class Mirror:
    def __init__(self, root: str, config, overwrite=False):
        if not isinstance(config, MirrorConfig):
            config = MirrorConfig(config)
        self.config = config

        self.root = root
        self.overwrite = overwrite
        self.failed_releases = self.config.releases

    def pull_releases(self):
        failed_releases = self.failed_releases.copy()
        for item in self.failed_releases:
            filepath = self.config.get_outpath(*item)
            out = os.path.join(self.root, filepath)

            logging.info(f"start to pull {out}")
            overwrite = True if item[0] == "latest" else self.overwrite
            rst = download_package(*item, out, overwrite)
            if rst:
                assert item in self.failed_releases
                failed_releases.remove(item)
        self.failed_releases = failed_releases
