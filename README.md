# JILL.py

![](https://img.shields.io/badge/system-Windows%7CmacOS%7CLinux%7CFreeBSD-yellowgreen)
![](https://img.shields.io/badge/arch-i686%7Cx86__64%7CARMv7%7CARMv8-yellowgreen)

[![py version](https://img.shields.io/pypi/pyversions/jill.svg?logo=python&logoColor=white)](https://pypi.org/project/jill)
[![version](https://img.shields.io/pypi/v/jill.svg)](https://github.com/johnnychen94/jill.py/releases)
[![Actions Status](https://github.com/johnnychen94/jill.py/workflows/Unit%20test/badge.svg
)](https://github.com/johnnychen94/jill.py/actions)
[![codecov](https://codecov.io/gh/johnnychen94/jill.py/branch/master/graph/badge.svg)](https://codecov.io/gh/johnnychen94/jill.py)
[![release-date](https://img.shields.io/github/release-date/johnnychen94/jill.py)](https://github.com/johnnychen94/jill.py/releases)

The enhanced Python fork of [JILL](https://github.com/abelsiqueira/jill) -- Julia Installer for Linux (MacOS, Windows and FreeBSD) -- Light

## Features

_let's make a simple and stupid julia installer_ [中文说明](README_zh.md)

* download *latest* Julia release from *nearest* mirror server.
* across multiple platforms.
* manage multiple julia releases.

## Installation

First you'll need to install `jill` using pip: `pip install jill --user -U`

Note that `Python >= 3.6` is required. For base docker images, you also need to make sure `wget` and `gnupg` are installed.

## Usage examples for most users

TL;DR `jill install [version]` covers most of your need.

<details>
<summary>installation demo</summary>
<img class="install" src="screenshots/install_demo.png"/>
</details>

When you type `jill install`, it does the following things:

1. query latest stable release, it's `1.3.1` at the time of writing.
2. download, verify and install julia `1.3.1`
3. make alias: `julia-1` and `julia-1.3`

Valid `version` syntax:

- `stable`: latest stable release
- `1`: latest stable `1.y.z` release
- `1.2`: latest stable `1.2.z` release
- `1.2.3`/`1.2.3-rc1`: as it is
- `nightly`/`latest`: nightly builds

Here's a list of slightly advanced usages that you may be interested in:

* download only:
    - latest stable release for current system: `jill download`
    - specific system: `jill download --sys freebsd --arch x86_64`
    - download Julia to specific dir: `jill download --outdir another/dir`
* install Julia for current system:
    - (linux only) system-wide for root: `sudo jill install`
    - upgrade from older julia version: `jill install --upgrade`
    - don't need interactive promopt: `jill install --confirm`
* upstream:
    - from specific upstream: `jill install --upstream Official`
    - find out all registered upstreams: `jill upstream`
    - add a private upstream: make a modifed copy of [public registry](jill/config/sources.json) at:
        * Linux, MacOS and FreeBSD: `~/.config/jill/sources.json`
        * Windows: `~/AppData/Local/julias/sources.json`

You can find a more verbose documentation using `jill [COMMAND] -h` (e.g., `jill download -h`)

## For who are interested in setting up a new release mirror

### Mirror

`jill mirror [outdir]`:

1. checks if there're new julia releases
2. downloads all releases Julia releases into `outdir` (default `./julia_pkg`)
3. (Optional): with flag `--period PERIOD`, it will repeat step 1 and 2 every `PERIOD` seconds

You can create a `mirror.json` in current folder to override the default mirror
behaviors. The [mirror configuration example](mirror.example.json) shows the default
values for all possible configurable items.

Repository [jill-mirror](https://github.com/johnnychen94/julia-mirror) provides an easy to
start `docker-compose.yml` for you to start with, which is just a simple docker image built
upon `jill mirror`.

### Register new mirror

If it's an public mirror and you want to share it worldwide. You can add an entry to the
[public registry](jill/config/sources.json), make a PR, then I will tag a new release for that.

If it's an internal mirror and you don't plan to make it public, you can create a config
file at `~/.config/jill/sources.json` locally. The contents will be appended to
the public registry and overwrite already existing items if there are.

In the registry config file, a new mirror is a dictionary in the `upstream` field:

* `name`: a distinguishable mirror name
* `urls`: URL template to retrive Julia release
* `latest_urls`: URL template to retrive the nightly build of Julia release

### Placeholders

Placeholders are used to register new mirrors. For example, the stable release url of
the "Official" release server provided by [Julialang.org](https://julialang.org/) is
`"https://julialang-s3.julialang.org/bin/$sys/$arch/$minor_version/$filename"`

There're several predefined placeholders for various systems and architectures:

* `system`: `windows`, `macos`, `linux`, `freebsd`
* `sys`: `winnt`, `mac`, `linux`, `freebsd`
* `os`: `win`, `mac`, `linux`, `freebsd`
* `architecture`: `x86_64`, `i686`, `ARMv7`, `ARMv8`
* `arch`: `x86`, `x64`, `armv7l`, `aarch64`
* `osarch`: `win32`, `win64`, `mac64`, `linux-armv7l`, `linux-aarch64`
* `osbit`: `win32`, `win64`, `linux32`, `linux64`, `linuxaarch64`
* `bit`: `32`, `64`
* `extension`: `exe`, `tar.gz`, `dmg` (no leading `.`)

There're also placeholders for versions:

* `patch_version`: `1.2.3`, `latest`
* `minor_version`: `1.2`, `latest`
* `major_version`: `1`
* `version`: `1.2.3-pre`, `latest` (no leading `v`)
* `vpatch_version`: `v1.2.3`, `latest`
* `vminor_version`: `v1.2`, `latest`
* `vmajor_version`: `v1`, `latest`

To keep consistent names with official releases, you can use predefined name placeholders:

* stable release `filename`: `julia-$version-$osarch.$extension`
* nightly release `latest_filename`: `"julia-latest-$osbit.$extension"`
