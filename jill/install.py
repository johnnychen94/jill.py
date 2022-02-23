from .utils.defaults import default_depot_path, default_install_dir, default_symlink_dir
from .utils.filters import f_major_version, f_minor_version
from .utils import query_yes_no
from .utils import current_architecture, current_system, current_libc
from .utils import latest_version
from .utils import DmgMounter, TarMounter
from .utils import Version
from .utils import verify_upstream
from .utils import color, show_verbose
from .download import download_package

import os
import re
import shutil
import subprocess


def is_installed(version, check_symlinks=True):
    """
        check if the required version is already installed.
    """
    check_list = ["julia"]
    if version == "latest":
        check_list.append("julia-latest")
    if version != "latest" and check_symlinks:
        check_list.extend([f"julia-{f_major_version(version)}",
                           f"julia-{f_minor_version(version)}"])

    for path in check_list:
        if Version(get_exec_version(shutil.which(path))) != Version(version):
            return False
    return True


def get_exec_version(path):
    ver_cmd = [path, "--version"]
    try:
        # outputs: "julia version 1.4.0-rc1"
        version = subprocess.check_output(ver_cmd).decode("utf-8")
        version = version.lower().split("version")[-1].strip()
    except:  # nopep8
        # in case it fails in any situation: invalid target or command(.cmd)
        # issue: https://github.com/abelsiqueira/jill/issues/25
        version = "0.0.1"
    return version


def check_installer(installer_path, ext):
    filename = os.path.basename(installer_path)
    if not filename.endswith(ext):
        msg = f"The installer {filename} should be {ext} file"
        raise ValueError(msg)


def last_julia_version(version=None):
    # version should follow semantic version syntax
    def sort_key(ver):
        return float(ver.lstrip("v"))

    version = float(f_minor_version(version)) if version else 999.999
    proj_versions = os.listdir(os.path.join(default_depot_path(),
                                            "environments"))
    proj_versions = [x for x in proj_versions if re.fullmatch(r"v\d+\.\d+", x)]
    proj_versions = sorted(filter(lambda ver: sort_key(ver) < version,
                                  proj_versions),
                           key=sort_key)
    if proj_versions:
        return proj_versions[-1]
    else:
        return None


def make_symlinks(src_bin, symlink_dir, version):
    if not os.path.isfile(src_bin):
        raise(ValueError(f"{src_bin} doesn't exist."))

    system = current_system()
    if symlink_dir not in map(os.path.normpath, os.environ["PATH"].split(os.pathsep)):
        print(f"add {symlink_dir} to PATH")
        if system == "winnt":
            # FIXME: this alse copies system PATH to user PATH
            subprocess.run(["powershell.exe",
                            "setx", "PATH", f'"$env:PATH;{symlink_dir}"'])
        else:
            msg = "~/.bashrc will be modified"
            msg += "\nif you're not using BASH, then you'll need manually"
            msg += f" add {symlink_dir} to your PATH"
            print(msg)

            rc_file = os.path.expanduser("~/.bashrc")
            with open(rc_file, "a") as file:
                file.writelines("\n# added by jill\n")
                file.writelines(f"export PATH={symlink_dir}:$PATH\n")
        print(f"you need to restart your current shell to update PATH")

    os.makedirs(symlink_dir, exist_ok=True)

    new_ver = Version(get_exec_version(src_bin))
    if version == "latest":
        # issue 11: don't symlink to julia
        link_list = ["julia-latest"]
    elif len(Version(version).build) > 0:
        link_list = ["julia-dev"]
    elif len(new_ver.prerelease) > 0:
        # issue #76
        # - it is usually unwanted to symlink unstable release to `julia` and `julia-x`
        # - still symlink to `julia-x.y` because otherwise there is no way to access the unstable
        #   release.
        link_list = [f"julia-{f_minor_version(version)}"]
    else:
        link_list = [f"julia-{f(version)}" for f in (f_major_version,
                                                     f_minor_version)]
        link_list.append("julia")

    for linkname in link_list:
        linkpath = os.path.join(symlink_dir, linkname)
        if current_system() == "winnt":
            linkpath += ".cmd"
        # symlink rules:
        # 1. always symlink latest
        # 2. only make new symlink if it's a newer version
        #   - julia      --> latest stable X.Y.Z
        #   - julia-1    --> latest stable 1.Y.Z
        #   - julia-1.0  --> latest stable 1.0.Z
        #   - don't make symlink to patch level
        if os.path.exists(linkpath) or os.path.islink(linkpath):
            if (os.path.islink(linkpath) and
                    os.readlink(linkpath) == src_bin):
                # happens when installing a new patch version
                continue

            old_ver = Version(get_exec_version(linkpath))
            if show_verbose():
                print(f"old symlink version: {old_ver}")
                print(f"new installation version: {new_ver}")
            if old_ver > new_ver:
                # if two versions are the same, use the new one
                continue

            msg = f"{color.YELLOW}remove old symlink"
            msg += f" {linkname}{color.END}"
            print(msg)
            os.remove(linkpath)
        print(f"{color.GREEN}make new symlink {linkpath}{color.END}")
        if current_system() == "winnt":
            with open(linkpath, 'w') as f:
                # create a cmd file to mimic how we do symlinks in linux
                f.writelines(['@echo off\n', f'"{src_bin}" %*'])
        else:
            os.symlink(src_bin, linkpath)


def copy_root_project(version):
    mver = f_minor_version(version)
    old_ver = last_julia_version(version)
    if old_ver is None:
        print(
            f"Can't find available old root project for version {version}")
        return None

    env_path = os.path.join(default_depot_path(), "environments")
    src_path = os.path.join(env_path, old_ver)
    dest_path = os.path.join(env_path, f"v{mver}")

    if src_path == dest_path:
        return None

    if os.path.exists(dest_path):
        bak_path = os.path.join(env_path, f"v{mver}.bak")
        if os.path.exists(bak_path):
            print(f"{color.YELLOW}delete old backup {bak_path}{color.END}")
            shutil.rmtree(bak_path)
        shutil.move(dest_path, bak_path)
        print(f"{color.YELLOW}move {dest_path} to {bak_path}{color.END}")
    shutil.copytree(src_path, dest_path)


def install_julia_tarball(package_path,
                          install_dir,
                          symlink_dir,
                          version,
                          upgrade):
    check_installer(package_path, ".tar.gz")

    if re.match("(.*)\+(\w+)$", version):
        # We want a different folder name for commit builds so that we can have
        # julia-dev and julia-latest points to two different julia versions
        suffix = 'dev'
    else:
        suffix = f_minor_version(version)

    with TarMounter(package_path) as root:
        src_path = root
        dest_path = os.path.join(install_dir, f"julia-{suffix}")
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
            msg = f"{color.YELLOW}remove previous Julia installation:"
            msg += f" {dest_path}{color.END}"
            print(msg)
        # preserve lib symlinks, otherwise it might cause troubles
        # see also: https://github.com/JuliaGPU/CUDA.jl/issues/249
        shutil.copytree(src_path, dest_path, symlinks=True)
        print(f"{color.GREEN}install Julia to {dest_path}{color.END}")
    os.chmod(dest_path, 0o755)  # issue 12
    bin_path = os.path.join(dest_path, "bin", "julia")
    if current_system() == 'winnt':
        bin_path += '.exe'
    make_symlinks(bin_path, symlink_dir, version)
    if upgrade:
        copy_root_project(version)
    return True


def install_julia_dmg(package_path,
                      install_dir,
                      symlink_dir,
                      version,
                      upgrade):
    check_installer(package_path, ".dmg")

    with DmgMounter(package_path) as root:
        # mounted image contents:
        #   ['.VolumeIcon.icns', 'Applications', 'Julia-1.3.app']
        appname = next(filter(lambda x: x.lower().startswith('julia'),
                              os.listdir(root)))
        src_path = os.path.join(root, appname)
        dest_path = os.path.join(install_dir, appname)
        if os.path.exists(dest_path):
            msg = f"{color.YELLOW}remove previous Julia installation:"
            msg += f" {dest_path}{color.END}"
            print(msg)
            shutil.rmtree(dest_path)
        # preserve lib symlinks, otherwise it might cause troubles
        # see also: https://github.com/JuliaGPU/CUDA.jl/issues/249
        shutil.copytree(src_path, dest_path, symlinks=True)
        print(f"{color.GREEN}install Julia to {dest_path}{color.END}")
    bin_path = os.path.join(dest_path,
                            "Contents", "Resources", "julia", "bin", "julia")
    make_symlinks(bin_path, symlink_dir, version)
    if upgrade:
        copy_root_project(version)
    return True


def install_julia_exe(package_path,
                      install_dir,
                      symlink_dir,
                      version,
                      upgrade):
    check_installer(package_path, ".exe")

    dest_path = os.path.join(install_dir,
                             f"julia-{f_minor_version(version)}")
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path, ignore_errors=True)
        msg = f"{color.YELLOW}remove previous Julia installation:"
        msg += f" {dest_path}{color.END}"
        print(msg)

    # build system changes for windows after 1.4
    # https://github.com/JuliaLang/julia/blob/release-1.4/NEWS.md#build-system-changes
    if Version(version).next_patch() < Version("1.4.0"):
        # it's always false if version == "latest"
        subprocess.check_output([f'{package_path}',
                                 '/S', f'/D={dest_path}'])
    else:
        subprocess.check_output([f'{package_path}',
                                 '/VERYSILENT',
                                 f'/DIR={dest_path}'])
    print(f"{color.GREEN}install Julia to {dest_path}{color.END}")
    bin_path = os.path.join(dest_path, "bin", "julia.exe")
    make_symlinks(bin_path, symlink_dir, version)
    if upgrade:
        copy_root_project(version)
    return True


def hello_msg():
    msg = f"{color.BOLD}JILL - Julia Installer 4 Linux"
    msg += f" (MacOS, Windows and FreeBSD) -- Light{color.END}\n"
    print(msg)


def install_julia(version=None, *,
                  preferred_arch=None,
                  install_dir=None,
                  symlink_dir=None,
                  upgrade=False,
                  upstream=None,
                  unstable=False,
                  keep_downloads=False,
                  confirm=False,
                  reinstall=False,
                  bypass_ssl=False):
    """
    Install the Julia programming language for your current system

    `jill install [version]` would satisfy most of your use cases, try it first
    and then read description of other arguments. `version` is optional, valid
    version syntax for it is:

    * `stable`: latest stable Julia release. This is the _default_ option.
    * `1`: latest `1.y.z` Julia release.
    * `1.0`: latest `1.0.z` Julia release.
    * `1.4.0-rc1`: as it is.
    * `latest`/`nightly`: the nightly builds from source code.

    For Linux/FreeBSD systems, if you run this command with `root` account,
    then it will install Julia system-widely.

    To download from a private mirror, please check `jill download -h`.

    Arguments:
      version:
        The Julia version you want to install.
      preferred_arch:
        (Experimental): add `--preferred-arch arm64` to download the native version for macOS the
        M-series Processor. For any other platform, this flag is ignored.
      upstream:
        manually choose a download upstream. For example, set it to "Official"
        if you want to download from JuliaComputing's s3 buckets.
      upgrade:
        add `--upgrade` flag also copy the root environment from an older
        Julia version.
      unstable:
        add `--unstable` flag to allow installation of unstable releases for auto version
        query. For example, `jill install --unstable` might give you unstable installation
        like `1.7.0-beta1`. Note that if you explicitly pass the unstable version, e.g.,
        `jill install 1.7.0-beta1`, it will still work.
      keep_downloads:
        add `--keep_downloads` flag to not remove downloaded releases.
      confirm: add `--confirm` flag to skip interactive prompt.
      reinstall:
        jill will skip the installation if the required Julia version already exists,
        add `--reinstall` flag to force the reinstallation.
      install_dir:
        where you want julia packages installed.
      symlink_dir:
        where you want symlinks(e.g., `julia`, `julia-1`) placed.
      bypass_ssl:
        add `--bypass-ssl` flag to skip SSL certificate validation.
    """
    install_dir = install_dir if install_dir else default_install_dir()
    install_dir = os.path.abspath(install_dir)
    symlink_dir = symlink_dir if symlink_dir else default_symlink_dir()
    symlink_dir = os.path.normpath(os.path.abspath(symlink_dir))
    system, arch = current_system(), current_architecture()
    version = str(version) if (version or str(version) == "0") else ''
    version = "latest" if version == "nightly" else version
    version = "" if version == "stable" else version
    upstream = upstream if upstream else os.environ.get("JILL_UPSTREAM", None)

    if system == "linux" and current_libc() == "musl":
        # currently Julia tags musl as a system, e.g.,
        # https://julialang-s3.julialang.org/bin/musl/x64/1.5/julia-1.5.1-musl-x86_64.tar.gz
        system = "musl"
    if system == "mac" and arch == "aarch64":
        if preferred_arch:  # preferred architecture for macOS
            if preferred_arch.lower() in ["aarch64", "arm64"]:
                arch = "aarch64"
            elif preferred_arch.lower() in ["x86_64", "x64"]:
                arch = "x86_64"
            else:
                raise ValueError(
                    "Unrecognized value {preferred_arch} for flag `--preferred-arch`")
        else:
            # Until Julia has tier-1 support for the apple silicon, we ship the intel version by default.
            # https://github.com/johnnychen94/jill.py/issues/102
            # TODO(johnnychen94): provide a way to install the native version.
            msg = "Apple silicon is still tier-3 support, installing the Intel version by default."
            msg += "\nAdd `--preferred-arch arm64` flag to install the native version."
            print(f"{color.YELLOW}{msg}{color.END}")
            arch = "x86_64"

    hello_msg()
    if system == "winnt":
        install_dir = install_dir.replace("\\\\", "\\").strip('\'"')
    if not confirm:
        version_str = version if version else "latest stable release"
        question = "jill will:\n"
        question += f"  1) install Julia {version_str} for {system}-{arch}"
        question += f" into {color.UNDERLINE}{install_dir}{color.END}\n"
        question += f"  2) make symlinks in {color.UNDERLINE}{symlink_dir}{color.END}\n"
        question += f"You may need to manually add {color.UNDERLINE}{symlink_dir}{color.END} to PATH\n"
        question += "Continue installation?"
        to_continue = query_yes_no(question)
        if not to_continue:
            return False

    if upstream:
        verify_upstream(upstream)
    wrong_args = False
    try:
        version = latest_version(
            version, system, arch, upstream=upstream, stable_only=not unstable)
    except ValueError:
        # hide the nested error stack :P
        wrong_args = True
    if wrong_args:
        msg = f"wrong version(>= 0.6.0) argument: {version}\n"
        msg += f"Example: `jill install 1`"
        raise(ValueError(msg))

    if not reinstall and is_installed(version):
        print(f"julia {version} already installed.")
        return True

    overwrite = True if version == "latest" else False
    print(f"{color.BOLD}----- Download Julia -----{color.END}")
    package_path = download_package(version,
                                    system,
                                    arch,
                                    upstream=upstream,
                                    overwrite=overwrite,
                                    bypass_ssl=bypass_ssl)
    if not package_path:
        return False

    if package_path.endswith(".dmg"):
        installer = install_julia_dmg
    elif package_path.endswith(".tar.gz"):
        installer = install_julia_tarball
    elif package_path.endswith(".exe"):
        installer = install_julia_exe
    else:
        print(f"{color.RED}Unsupported file format for {package_path}{color.END}.")

    print(f"{color.BOLD}----- Install Julia -----{color.END}")
    installer(package_path, install_dir, symlink_dir, version, upgrade)

    if not keep_downloads:
        print(f"{color.BOLD}----- Post Installation -----{color.END}")
        print("remove downloaded files...")
        print(f"remove {package_path}")
        os.remove(package_path)
        gpg_signature_file = package_path + ".asc"
        if os.path.exists(gpg_signature_file):
            print(f"remove {gpg_signature_file}")
            os.remove(gpg_signature_file)
    print(f"{color.GREEN}Done!{color.END}")
