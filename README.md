# JILL.py

<p>
  <img width="150" align='right' src="logo.png">
</p>

_The enhanced Python fork of [JILL](https://github.com/abelsiqueira/jill) -- Julia Installer for Linux (and every other platform) -- Light_

![](https://img.shields.io/badge/system-Windows%7CmacOS%7CLinux%7CFreeBSD-yellowgreen)
![](https://img.shields.io/badge/arch-i686%7Cx86__64%7CARMv7%7CARMv8-yellowgreen)

[![py version](https://img.shields.io/pypi/pyversions/jill.svg?logo=python&logoColor=white)](https://pypi.org/project/jill)
[![version](https://img.shields.io/pypi/v/jill.svg)](https://github.com/johnnychen94/jill.py/releases)
[![Actions Status](https://github.com/johnnychen94/jill.py/workflows/Unit%20test/badge.svg
)](https://github.com/johnnychen94/jill.py/actions)
[![codecov](https://codecov.io/gh/johnnychen94/jill.py/branch/master/graph/badge.svg)](https://codecov.io/gh/johnnychen94/jill.py)
[![release-date](https://img.shields.io/github/release-date/johnnychen94/jill.py)](https://github.com/johnnychen94/jill.py/releases)
[![中文README](https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87-blue)](README_zh.md)

## Features

* download Julia releases from the *nearest* mirror server
* support all platforms and architectures
* manage multiple julia releases
* easy-to-use CLI tool

[![asciicast](https://asciinema.org/a/432654.svg)](https://asciinema.org/a/432654)

## Install JILL

For the first time users of `jill`, you will need to install it using `pip`: `pip install jill
--user -U`. Also use this to upgrade JILL version.

`Python >= 3.6` is required. For base docker images, you also need to make sure `wget` and `gnupg`
are installed.


## Installing Julias

When you type `jill install`, it does the following things:

1. query the latest version
2. download, verify, and install julia
3. make symlinks, e.g., `julia`, `julia-1`, `julia-1.6`

For common Julia users:

* Get the latest stable release: `jill install`
* Get the latest 1.y.z release: `jill install 1`
* Get the latest 1.6.z release: `jill install 1.6`
* Get the specific version: `jill install 1.6.2`, `jill install 1.7.0-beta3`
* Get the latest release (including unstable ones): `jill install --unstable`

For Julia developers and maintainers:

* Get the nightly builds: `jill install latest`. This gives you `julia-latest`.
* Checkout CI build artifacts of specific commit in the [Julia Repository]: `jill install
  1.8.0+cc4be25c` (`<major>.<minor>.<patch>+<build>` with at least the first 7 characters of the
  hash). This gives you `julia-dev`.

Some flags that can be useful:

* No confirmation before installation: `jill install --confirm`
* Download from Official source: `jill install --upstream Official`
* Keep downloaded contents after installation: `jill install --keep_downloads`
* Force a reinstallation: `jill install --reinstall`

## The symlinks

To start Julia, you can use predefined JILL symlinks such as `julia`. `jill install` uses the following rule makes sure
that you're always using the latest stable release.

Stable releases:

* `julia` points to the latest Julia release.
* `julia-1` points to the latest 1.y.z Julia release.
* `julia-1.6` points to the latest 1.6.z Julia release.

For unstable releases such as `1.7.0-beta3`, installing it via `jill install 1.7 --unstable` or
`jill install 1.7.0-beta3`  will only give you `julia-1.7`; it won't make symlinks for `julia` or
`julia-1`.

To dance on edge:

* `julia-latest` points to the nightly build from `jill install latest`
* `julia-dev` points to the julia CI build artifacts from, for example, `jill install 1.8.0+cc4be25c`.

### List symlinks and their target versions

`jill list [version]` gives you every symlinks and their target Julia versions.

![list](https://user-images.githubusercontent.com/8684355/131207375-8b355e2b-3a67-4b70-8d2d-83623ae1e451.png)

### Change symlink target

For non-windows system, you are free to use `ln` command to change the symlink targets. For Windows
it uses an entry `.cmd` file for this so you'll need to copy them. In the meantime, `jill switch`
provides a simple and unified way to do this:

* `jill switch 1.6`: let `julia` points to the latest julia 1.6.z release.
* `jill switch <path/to/my/own/julia/executable>`: let `julia` points to custom executables.
* `jill switch 1.6 --target julia-1`: let `julia-1` points to the latest julia 1.6.z release.

## About downloading upstreams

By default, JILL tries to be smart and will download contents from the _nearest_ upstream. You can
get the information of all upstreams via `jill upstream`. Here's what I get in my laptop, I live in
China so the official upstreams aren't so accessible for me :(

![upstream](https://user-images.githubusercontent.com/8684355/131207372-03220bc4-bf79-408d-b386-ef9b41524ccd.png)

To temporarily disable this feature, you can use flag `--upstream <server_name>`. For instance,
`jill install --upstream Official` will faithfully download from the official julialang s3 bucket.

To permanently disable this feature, you can set environment variable `JILL_UPSTREAM`.

Note that flag is of higher priority than environment variable. For example, if `JILL_UPSTREAM` is
set to mirror server `"TUNA"`, you can still download from the official source via `jill install
--upstream Official`.

## About installation and symlink directories

Here's the default JILL installation and symlink directories:

| system         | installation directory    | symlink directory            |
| -------------- | ------------------------- | ---------------------------- |
| macOS          | `/Applications`           | `~/.local/bin`               |
| Linux/FreeBSD  | `~/packages/julias`       | `~/.local/bin`               |
| Windows        | `~\AppData\Local\julias`  | `~\AppData\Local\julias\bin` |

For example, on Linux `jill install 1.6.2` will have a julia folder in `~/packages/julias/julia-1.6`
and symlinks `julia`/`julia-1`/`julia-1.6` created in `~/.local/bin`.

Particularly, if you're using `jill` as `root` user, you will do a system-wide installation:

* Installation directory will be `/opt/julias` for Linux/FreeBSD.
* Symlink directory will be `/usr/local/bin` for Linux/FreeBSD/macOS.

To change the default JILL installation and symlink directories, you can set environment variables
`JILL_INSTALL_DIR` and `JILL_SYMLINK_DIR`.

**(Deprecated)** `jill install` also provides two flag `--install_dir <dirpath>` and `--symlink_dir
<dirpath>`, they have higher priority than the environment variables `JILL_INSTALL_DIR` and
`JILL_SYMLINK_DIR`.

## JILL environment variables

`jill` is made as a convenient tool and it can sometimes be annoying passing flags to it. There are
some predefined environment variables that you can use to set the default values:

* Specify a default downloading upstream `JILL_UPSTREAM`: `--upstream`
* Override default symlink directory `JILL_SYMLINK_DIR`: `--symlink_dir`
* Override default installation directory `JILL_INSTALL_DIR`: `--install_dir`

The flag version has higher priority than the environment variable version.

---

## Advanced: Example with cron

If you're tired of seeing `(xx days old master)` in your nightly build version, then `jill` can
make your nightly build always the latest version using `cron`:

```bash
# /etc/cron.d/jill
PATH=/usr/local/bin:/usr/sbin:/usr/sbin:/usr/bin:/sbin:/bin

# install a fresh nightly build every day
* 0 * * * root jill install latest --confirm --upstream Official
```

## Advanced: Registering a new public releases upstream

If it's an public mirror and you want to share it worldwide to other users of JILL. You can add an
entry to the [public registry](jill/config/sources.json), make a PR, then I will tag a new release
for that.

Please check [the `sources.json` format](sources_format.md) for more detailed information on the
format.

## Advanced: Specifying custom (private) downloading upstream

To add new private upstream, you can create a file `~/.config/jill/sources.json` (fow Windows it is
`~/AppData/Local/julias/sources.json`) and add your own upstream configuration just like the JILL
[`sources.json`](jill/config/sources.json) does. Once this is done JILL will recognize this new
upstream entry.

Please check [the `sources.json` format](sources_format.md) for more detailed information on the
format.

## Advanced: make a Julia release mirror

There are two ways to do so:

* use `aws s3 sync`, this should be the easiest way to do so I highly recommend this.
* **(Deprecated)** use `jill mirror` command with [mirror config example](mirror.example.json). I
  didn't know about the `aws s3 sync` stuff when I implemented this.

The Julia release mirror does not contain Julia package contents, to mirror all the Julia packages
and artifacts (which requires >1.5Tb storage), you can use [StorageMirrorServer.jl].

## Advanced: The Python API

`jill.py` also provides a set of Python API:

```python
from jill.install import install_julia
from jill.download import download_package

# equivalent to `jill install --confirm`
install_julia(confirm=True)
# equivalent to `jill download`
download_package()
```

You can read its docstring (e.g., `?install_julia`) for more information.

## FAQs

### Why you should use JILL?

Distro package managers (e.g., `apt`, `pac`) is likely to provide a broken Julia with incorrect
binary dependencies (e.g., LLVM ) versions. Hence it's recommended to download and extract the
Julia binary provided in [Julia Downloads](https://julialang.org/downloads/). `jill.py` doesn't do
anything magical, but just makes such operation even stupid.

### Why I make the python fork of JILL?

At first I found myself needing a simple tool to download and install Julia on my macbook and
servers in our lab, I made my own shell scripts and I'd like to share it with others. Then I found
the [jill.sh][JILL-sh] project, Abel knows a lot shell so I decide to contribute my macOS Julia
installer to `jill.sh`.

There are three main reasons for why I decided to start my Python fork:

* I live in China. Downloading resources from GitHub and AWS s3 buckets is a painful experience.
  Thus I want to support downloading from mirror servers. Adding mirror server support to jill.sh is
  quite complicated and can easily become a maintenance nightmare.
* I want to make a cross platform installer that everyone can use, not just Linux/macOS users. Shell
  scripts doesn't allow this as far as I can tell. In contrast, Python allows this.
* Most importantly, back to when I start this project, I knew very little shell, I knew nothing
  about C/C++/Rust/Go and whatever you think a good solution is. I happen to knew a few Python.

For some "obvious" reason, Julia People don't like Python and I understand it. (I also don't like
Python after being advanced Julia user for more than 3 years) But to be honest, revisiting this
project, I find using Python is one of the best-made decision during the entire project. Here is the
reason: no matter how you enjoy Julia (or C++, Rust), Python is one of the best successful
programming language for sever maintenance purpose. Users can easily found tons of "how-to"
solutions about Python and it's easy to write, deploy, and ship Python codes to the world via PyPI.

And again, I live in China so I want to rely on services that are easily accessible in China, PyPI
is, GitHub and AWS S3 bucket aren't. A recent Julia installer project [juliaup] written in Rust
solves the Python dependency problem very well, but the tradeoff is that `juliaup` needs its own
distributing system (currently GitHub and S3 bucket) to make sure it can be reliably downloaded to
user machine. And for this it just won't be as good as PyPI in the foreseeable future.

### Is it safe to use `jill.py`?

Yes, `jill.py` use GPG to check every tarballs after downloading. Also, `*.dmg`/`*.pkg` for macOS
and `.exe` for Windows are already signed.

### What's the difference between `jill.sh` and `jill.py`

[`jill.sh`][JILL-sh] is a shell script that works quite well on Linux x86/x64 machines. `jill.py` is
an enhanced python package that focus on Julia installation and version management, and brings a
unified user experience on all platforms.

### Why `julia` fails to start

The symlink `julia` are stored in [JILL predefined symlinks
dir](#About-installation-and-symlink-directories) thus you have to make sure this folder is in
`PATH`. Search "how to add folder to PATH on xxx system" you will get a lot of solutions.

### How do I use multiple patches releases (e.g., `1.6.1` and `1.6.2`)

Generally, you should not care about patch version differences so `jill.py` make it explicitly that
only one of 1.6.x can exist. If you insist to have multiple patch versions, you could use `jill
install --install_dir <some_other_folder>` to install Julia in other folder, and then manually make
a symlink back. As I just said, in most cases, common users should not care about this patch version
difference and should just use the latest patch release.

### How to only download contents without installation?

Use `jill download [version] [--sys <system>] [--arch <arch>]`. Check `jill download --help` for
more details.

### Linux with musl libc

For Julia (>= 1.5.0) in Linux with musl libc, you can just do `jill install` and it gives you the
right Julia binary. To download the musl libc binary using `jill download`, you will need to pass
`--sys musl` flag.

### MacOS with Apple silicon (M1)

Yes it's supported. Because macOS ARM version is still of tier-3 support, jill.py will by default
install the x86_64 version. If you want to use the ARM version, you can install it via `jill install
--preferred-arch arm64`.

### CERTIFICATE_VERIFY_FAILED error

If you're confident, try `jill install --bypass-ssl`.

<!-- URLS -->

[Julia Repository]: https://github.com/JuliaLang/julia
[JILL-sh]: https://github.com/abelsiqueira/jill
[juliaup]: https://github.com/JuliaLang/juliaup
[StorageMirrorServer.jl]: https://github.com/johnnychen94/StorageMirrorServer.jl
