# JILL.py

The Python fork of [JILL](https://github.com/abelsiqueira/jill) - Julia Installer 4 Linux (and MacOS) - Light

## Features

* download Julia release from nearest mirror server. Check [sources](jill/config/sources.json) for the list of all registered mirrors.
* install julia for Linux and MacOS (including nightly build: `latest`)
* easily set up a new release mirror 🚧

## Usage examples

* download:
    - download Julia for current system: `jill download 1.3.0`
    - download Julia for 32-bit linux: `jill download 1.3.0 linux i686`
    - download Julia to specific dir: `jill download 1.3.0 --outdir OUTDIR`
* install Julia for current system:
    - system-wide: `sudo jill install 1.3.0`
    - only for current user: `jill install 1.3.0`

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

## Mirror 🚧

`python mirror_daemon.py` downloads all Julia releases into `./julia_pkg`
