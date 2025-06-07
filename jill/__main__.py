from .download import download_package
from .install import install_julia
from .utils import show_upstream
from .list import list_julia
from .switch import switch_julia_target
import click
import logging
import os


@click.group()
def cli():
    """JILL -- Julia Installer for Linux (MacOS, Windows and FreeBSD) -- Light

    A command-line tool to install and manage Julia versions.
    """
    logging.basicConfig(filename=os.devnull, level=logging.DEBUG)


@cli.command()
@click.argument("version", required=False)
@click.option(
    "--preferred-arch",
    "--preferred_arch",
    help="Preferred architecture (e.g., arm64 for M-series Macs)",
)
@click.option(
    "--install-dir",
    "--install_dir",
    help="Installation directory",
)
@click.option(
    "--symlink-dir",
    "--symlink_dir",
    help="Symlink directory",
)
@click.option(
    "--upgrade/--no-upgrade",
    default=False,
    help="Upgrade existing installation and copy root environment from older version",
)
@click.option(
    "--upstream",
    help='Custom upstream URL (e.g., "Official" for JuliaComputing\'s s3 buckets)',
)
@click.option(
    "--unstable/--no-unstable",
    default=False,
    help="Allow installation of unstable releases (e.g., 1.7.0-beta1)",
)
@click.option(
    "--keep-downloads/--no-keep-downloads",
    "--keep_downloads/--no_keep_downloads",
    default=False,
    help="Keep downloaded files",
)
@click.option(
    "--confirm/--no-confirm",
    default=False,
    help="Skip interactive prompt",
)
@click.option(
    "--reinstall/--no-reinstall",
    default=False,
    help="Force reinstallation even if version exists",
)
@click.option(
    "--bypass-ssl/--no-bypass-ssl",
    "--bypass_ssl/--no_bypass_ssl",
    default=False,
    help="Skip SSL certificate validation",
)
@click.option(
    "--skip-symlinks/--no-skip-symlinks",
    "--skip_symlinks/--no_skip_symlinks",
    default=False,
    help="Skip creating symlinks",
)
def install(**kwargs):
    """Install Julia programming language.

    VERSION can be:
    * stable: latest stable Julia release (default)
    * 1: latest 1.y.z Julia release
    * 1.0: latest 1.0.z Julia release
    * 1.4.0-rc1: specific version
    * latest/nightly: nightly builds from source code

    For Linux/FreeBSD systems, if you run this command with root account,
    then it will install Julia system-widely.

    To download from a private mirror, please check `jill download -h`.
    """
    install_julia(**kwargs)


@cli.command()
@click.argument("version", required=False)
@click.option(
    "--upstream",
    help="Custom upstream URL",
)
@click.option(
    "--unstable/--no-unstable",
    default=False,
    help="Show unstable versions",
)
def list(**kwargs):
    """List installed Julia versions.

    VERSION is optional. If provided, it will filter versions matching the pattern.
    For example, `jill list 1` checks every symlink that matches `^julia-1`.
    (`julia` is excluded in this case.)
    """
    list_julia(**kwargs)


@cli.command()
@click.argument("version", required=False)
@click.option(
    "--sys",
    help="Target system (linux, musl, macos, freebsd, windows/winnt/win)",
)
@click.option(
    "--arch",
    help="Target architecture (i686/x86, x86_64/x64, ARMv7/armv7l, ARMv8/aarch64)",
)
@click.option(
    "--upstream",
    help='Custom upstream URL (e.g., "Official" for JuliaComputing\'s s3 buckets)',
)
@click.option(
    "--unstable/--no-unstable",
    default=False,
    help="Allow downloading unstable releases",
)
@click.option("--outdir", help="Output directory (default: current directory)")
@click.option(
    "--overwrite/--no-overwrite",
    default=False,
    help="Overwrite existing files",
)
@click.option(
    "--bypass-ssl/--no-bypass-ssl",
    "--bypass_ssl/--no_bypass_ssl",
    default=False,
    help="Skip SSL certificate validation",
)
def download(**kwargs):
    """Download Julia release from nearest servers.

    VERSION can be:
    * stable: latest stable Julia release (default)
    * 1: latest 1.y.z Julia release
    * 1.0: latest 1.0.z Julia release
    * 1.4.0-rc1: specific version
    * latest/nightly: nightly builds from source code

    For whatever reason, if you only want to download release from
    a specific upstream (e.g., from JuliaComputing), then you can use
    `--upstream` flag (e.g., `jill download --upstream Official`).

    To see a full list of upstream servers, please use `jill upstream`.

    If you're interested in downloading from an unregistered private
    mirror, you can provide a `sources.json` file to CONFIG_PATH and use
    `jill upstream` to check if your mirror is added. A config template
    can be found at:
    https://github.com/johnnychen94/jill.py/blob/master/jill/config/sources.json

    CONFIG_PATH:
    * windows: `~\\AppData\\Local\\julias\\sources.json`
    * other: `~/.config/jill/sources.json`
    """
    download_package(**kwargs)


@cli.command()
@click.argument("version_or_path", required=True)
@click.option("--target", default="julia", help="Target name (default: julia)")
@click.option("--symlink-dir", "--symlink_dir", help="Symlink directory")
def switch(**kwargs):
    """Switch Julia target version or path.

    VERSION_OR_PATH can be:
    * A path to a Julia executable
    * A version string in format "<major>" or "<major>.<minor>"
      For ambiguous input such as "1.10" (which could be interpreted as 1.1),
      you can either do `jill switch '"1.10"'` or `jill switch 1.10.0`
    """
    switch_julia_target(**kwargs)


@cli.command()
def upstream():
    """Show upstream information and available mirrors.

    This command displays information about available upstream servers
    and mirrors that can be used for downloading Julia releases.
    """
    show_upstream()


def main():
    cli()


if __name__ == "__main__":
    main()
