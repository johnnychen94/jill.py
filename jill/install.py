from .filters import f_major_version, f_minor_version, f_patch_version
from .filters import SPECIAL_VERSION_NAMES
from .download import download_package
from .interactive_utils import query_yes_no
from .sys_utils import current_architecture, current_system
from .version_utils import latest_version
from .mount_utils import DmgMounter, TarMounter
from semantic_version import Version
import os
import getpass
import shutil
import subprocess
import logging


def default_depot_path():
    return os.path.expanduser("~/.julia")


def default_symlink_dir():
    system = current_system()
    if system == "windows":
        return os.path.expanduser(r"~\AppData\Local\julias\bin")
    if getpass.getuser() == "root":
        # available to all users
        return "/usr/local/bin"
    else:
        # exclusive to current user
        return os.path.expanduser("~/.local/bin")


def default_install_dir():
    system = current_system()
    if system == "macos":
        return "/Applications"
    elif system in ["linux", "freebsd"]:
        if getpass.getuser() == "root":
            return "/opt/julias"
        else:
            return os.path.expanduser("~/packages/julias")
    elif system == "windows":
        return os.path.expanduser(r"~\AppData\Local\julias")
    else:
        raise ValueError(f"Unsupported system: {system}")


def get_exec_version(path):
    ver_cmd = [path, "--version"]
    try:
        # outputs: "julia version 1.4.0-rc1"
        version = subprocess.check_output(ver_cmd).decode("utf-8")
        version = version.lower().split("version")[-1].strip()
    except subprocess.CalledProcessError as e:
        # in case it's not executable
        logging.warn(e)
        version = "0.0.1"
    return version


def last_julia_version(version=None):
    # version should follow semantic version syntax
    def sort_key(ver):
        return float(ver.lstrip("v"))

    version = float(f_minor_version(version)) if version else 999.999
    proj_versions = os.listdir(os.path.join(default_depot_path(),
                                            "environments"))
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
    if symlink_dir not in os.environ["PATH"].split(os.pathsep):
        logging.info(f"add {symlink_dir} to PATH")
        if system == "windows":
            # FIXME: this alse copies system PATH to user PATH
            subprocess.run(["powershell.exe",
                            "setx", "PATH", f'"$env:PATH;{symlink_dir}"'])
        else:
            msg = "~/.bashrc will be modified"
            msg += ", if you're not using BASH, then you'll need manually"
            msg += f" add {symlink_dir} to your PATH\n"
            logging.info(msg)

            rc_file = os.path.expanduser("~/.bashrc")
            logging.info(f"{rc_file} is modified")
            with open(rc_file, "a") as file:
                file.writelines("\n# added by jill\n")
                file.writelines(f"export PATH={symlink_dir}:$PATH\n")
        logging.info(f"you need to restart your current shell to update PATH")

    os.makedirs(symlink_dir, exist_ok=True)

    if version in SPECIAL_VERSION_NAMES:
        # issue 11: don't symlink to julia
        link_list = [f"julia-{f_major_version(version)}"]
    else:
        link_list = [f"julia-{f(version)}" for f in (f_major_version,
                                                     f_minor_version,
                                                     f_patch_version)]
        link_list.append("julia")

    for linkname in link_list:
        linkpath = os.path.join(symlink_dir, linkname)
        if current_system() == "windows":
            linkpath += ".cmd"
        if os.path.exists(linkpath) or os.path.islink(linkpath):
            old_ver = get_exec_version(linkpath)
            if version != "latest" and Version(old_ver) > Version(version):
                continue
            logging.info(f"removing previous symlink {linkname}")
            os.remove(linkpath)
        logging.info(f"make symlink {linkpath}")
        if current_system() == "windows":
            with open(linkpath, 'w') as f:
                # create a cmd file to mimic how we do symlinks in linux
                f.writelines(["@echo off\n", f"{src_bin} %*"])
        else:
            os.symlink(src_bin, linkpath)


def copy_root_project(version):
    mver = f_minor_version(version)
    old_ver = last_julia_version(version)
    if old_ver is None:
        logging.info(
            f"Can't find available old root project for version f{version}")
        return None

    env_path = os.path.join(default_depot_path(), "environments")
    src_path = os.path.join(env_path, old_ver)
    dest_path = os.path.join(env_path, f"v{mver}")

    if os.path.exists(dest_path):
        bak_path = os.path.join(env_path, f"v{mver}.bak")
        logging.info(f"move {dest_path} to {bak_path}")
        shutil.move(dest_path, bak_path)
    shutil.copytree(src_path, dest_path)


def install_julia_linux(package_path,
                        install_dir,
                        symlink_dir,
                        version,
                        upgrade):
    mver = f_minor_version(version)
    with TarMounter(package_path) as root:
        src_path = root
        dest_path = os.path.join(install_dir, f"julia-{mver}")
        if os.path.exists(dest_path):
            logging.info(f"remove previous julia installation: {dest_path}")
            shutil.rmtree(dest_path)
        shutil.copytree(src_path, dest_path)
    os.chmod(dest_path, 0o755)  # issue 12
    bin_path = os.path.join(dest_path, "bin", "julia")
    make_symlinks(bin_path, symlink_dir, version)
    if upgrade:
        copy_root_project(version)
    return True


def install_julia_mac(package_path,
                      install_dir,
                      symlink_dir,
                      version,
                      upgrade):
    assert os.path.splitext(package_path)[1] == ".dmg"
    with DmgMounter(package_path) as root:
        # mounted image contents:
        #   ['.VolumeIcon.icns', 'Applications', 'Julia-1.3.app']
        appname = next(filter(lambda x: x.lower().startswith('julia'),
                              os.listdir(root)))
        src_path = os.path.join(root, appname)
        dest_path = os.path.join(install_dir, appname)
        if os.path.exists(dest_path):
            logging.info(f"remove previous julia installation: {dest_path}")
            shutil.rmtree(dest_path)
        shutil.copytree(src_path, dest_path)
    bin_path = os.path.join(dest_path,
                            "Contents", "Resources", "julia", "bin", "julia")
    make_symlinks(bin_path, symlink_dir, version)
    if upgrade:
        copy_root_project(version)
    return True


def install_julia_windows(package_path,
                          install_dir,
                          symlink_dir,
                          version,
                          upgrade):
    assert os.path.splitext(package_path)[1] == ".exe"

    dest_path = os.path.join(install_dir,
                             f"julia-{f_minor_version(version)}")
    if os.path.exists(dest_path):
        logging.info(f"remove previous julia installation: {dest_path}")
        shutil.rmtree(dest_path)

    if Version(version).next_patch() < Version("1.4.0"):
        subprocess.check_output([f'{package_path}',
                                 '/S', f'/D={dest_path}'])
    else:
        subprocess.check_output([f'{package_path}',
                                 '/VERYSILENT',
                                 f'/DIR={dest_path}'])
    bin_path = os.path.join(dest_path, "bin", "julia.exe")
    make_symlinks(bin_path, symlink_dir, version)
    if upgrade:
        copy_root_project(version)
    return True


def install_julia(version=None, *,
                  install_dir=None,
                  symlink_dir=None,
                  upgrade=False,
                  upstream=None,
                  keep_downloads=False,
                  confirm=False):
    """
    Install julia for Linux and MacOS

    Arguments:
      version: Option examples: 1, 1.2, 1.2.3, latest.
      upstream:
        manually choose a download upstream. For example, set it to "Official"
        if you want to download from JuliaComputing's s3 buckets.
      upgrade: True to also copy the root environment from older julia version.
      keep_downloads: True to not remove downloaded releases.
      confirm: add `--confirm` to skip interactive prompt.
    """
    install_dir = install_dir if install_dir else default_install_dir()
    symlink_dir = symlink_dir if symlink_dir else default_symlink_dir()
    system, arch = current_system(), current_architecture()
    version = str(version) if version else ''
    version = "latest" if version == "nightly" else version
    version = "" if version == "stable" else version

    if system == "windows":
        install_dir = install_dir.replace("\\\\", "\\")
    if not confirm:
        version_str = version if version else "latest release"
        question = "jill will:\n"
        question += f"    1) install Julia {version_str} for {system}-{arch}"
        question += f" into {install_dir}\n"
        question += f"    2) make symlinks in {symlink_dir}\n"
        question += f"    3) add {symlink_dir} to PATH if necessary\n"
        question += "Continue installation?"
        to_continue = query_yes_no(question)
        if not to_continue:
            return False

    overwrite = True if version == "latest" else False
    package_path = download_package(version, system, arch,
                                    upstream=upstream,
                                    overwrite=overwrite)
    version = latest_version(version, system, arch)
    if not package_path:
        return False

    if system == "macos":
        installer = install_julia_mac
    elif system in ["linux", "freebsd"]:
        installer = install_julia_linux
    elif system == "windows":
        installer = install_julia_windows
    else:
        raise ValueError(f"Unsupported system: {system}")

    installer(package_path, install_dir, symlink_dir, version, upgrade)

    if not keep_downloads:
        logging.info("remove downloaded files")
        logging.info(f"remove {package_path}")
        os.remove(package_path)
        gpg_signature_file = package_path + ".asc"
        if os.path.exists(gpg_signature_file):
            logging.info(f"remove {gpg_signature_file}")
            os.remove(gpg_signature_file)
    return True
