# JILL.py

[![py version](https://img.shields.io/pypi/pyversions/jill.svg?logo=python&logoColor=white)](https://pypi.org/project/jill) [![version](https://img.shields.io/pypi/v/jill.svg)](https://github.com/johnnychen94/jill.py/releases)
[![Actions Status](https://github.com/johnnychen94/jill.py/workflows/Unit%20test/badge.svg
)](https://github.com/johnnychen94/jill.py/actions)

The Python fork of [JILL](https://github.com/abelsiqueira/jill) - Julia Installer 4 Linux (and MacOS) - Light

## Features

* download *latest* Julia release from *nearest* mirror server. Check [sources](jill/config/sources.json) for the list of all registered mirrors.
* install julia for Linux and MacOS (including nightly build: `latest`)
* easily set up a new release mirror 🚧

## Installation

`pip install jill --user -U`

## Basic usage examples

* download:
    - latest stable release for current system: `jill download`
    - latest `1.y` version: `jill download 1`
    - latest `1.3.z` version: `jill download 1.3`
    - specific release version: `jill download --version 1.3.0`
    - specific system: `jill download --sys freebsd`
    - specific architecture: `jill download --arch i686`
    - download Julia to specific dir: `jill download --outdir another/dir`
* install Julia for current system:
    - system-wide: `sudo jill install` (make symlink in `/usr/bin`)
    - only for current user: `jill install` (make symlink in `~/.local/bin`)
    - don't need interactive promopt: `jill install --confirm`
* check if there're new Julia versions: `jill update`

## Mirror

`jill mirror` downloads all Julia releases into `./julia_pkg`

You can create a `mirror.json` in current folder to override the default mirror
behaviors. The [mirror configuration example](mirror.example.json) shows all possible
configurable items, where only `version` is required.

## Register new mirror

add an entry to `jill/config/sources.json`:

* `name`: a distinguishable mirror name
* `url`: URL template to retrive Julia release
* `filename` (optional): filename template. The default value is `julia-$patch_version-$osarch.$extension`

There're several predefined placeholders for various systems and architectures:

* `system`: `windows`, `macos`, `linux`, `freebsd`
* `sys`: `winnt`, `mac`, `linux`, `freebsd`
* `os`: `win`, `mac`, `linux`, `freebsd`
* `architecture`: `x86_64`, `i686`, `ARMv7`, `ARMv8`
* `arch`: `x86`, `x64`, `armv7l`, `aarch64`
* `osarch`: `win32`, `win64`, `mac64`, `linux-armv7l`, `linux-aarch64`
* `bit`: `32`, `64`
* `extension`: `exe`, `tar.gz`, `dmg` (no leading `.`)

There're also placeholders for versions:

* `patch_version`: `1.2.3`, `latest`
* `minor_version`: `1.2`, `latest`
* `major_version`: `1`
* `version`: `v1.2.3-pre`, `latest`
* `vpatch_version`: `v1.2.3`, `latest`
* `vminor_version`: `v1.2`, `latest`
* `vmajor_version`: `v1`, `latest`
