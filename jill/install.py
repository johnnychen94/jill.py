from .filters import f_major_version, f_minor_version, f_patch_version
from .download import download_package
from .interactive_utils import query_yes_no
from .sys_utils import current_architecture, current_system
from .version_utils import latest_version
from .mount_utils import DmgMounter, TarMounter
import os
import getpass
import shutil
import subprocess
import logging


def default_symlink_dir():
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
    elif system == "linux":
        if getpass.getuser() == "root":
            return "/opt/julias"
        else:
            return os.path.expanduser("~/packages/julias")
    else:
        raise ValueError(f"Unsupported system {system}")


def make_symlinks(src_bin, symlink_dir, version):
    if symlink_dir not in os.environ["PATH"].split(":"):
        logging.info(f"add {symlink_dir} to PATH")
        with open(os.path.expanduser("~/.bashrc"), "a") as file:
            file.writelines("\n# added by jill\n")
            file.writelines(f"export PATH={symlink_dir}:$PATH\n")
        logging.info(f"you need to do `. ~/.bashrc` to refresh your PATH")

    os.makedirs(symlink_dir, exist_ok=True)

    link_list = [f"julia-{f(version)}" for f in (f_major_version,
                                                 f_minor_version,
                                                 f_patch_version)]
    link_list.append("julia")

    for linkname in link_list:
        linkpath = os.path.join(symlink_dir, linkname)
        if os.path.exists(linkpath) or os.path.islink(linkpath):
            logging.info(f"removing previous symlink {linkname}")
            os.remove(linkpath)
        logging.info(f"make symlink {linkpath}")
        os.symlink(src_bin, linkpath)


def install_julia_linux(package_path, install_dir, symlink_dir, version):
    mver = f_minor_version(version)
    with TarMounter(package_path) as root:
        src_path = root
        dest_path = os.path.join(install_dir, f"julia-{mver}")
        if os.path.exists(dest_path):
            logging.info(f"remove previous {dest_path}")
            shutil.rmtree(dest_path)
        shutil.copytree(src_path, dest_path)
    bin_path = os.path.join(dest_path, "bin", "julia")
    make_symlinks(bin_path, symlink_dir, version)
    return True


def install_julia_mac(package_path, install_dir, symlink_dir, version):
    assert os.path.splitext(package_path)[1] == ".dmg"
    with DmgMounter(package_path) as root:
        # mounted image contents:
        #   ['.VolumeIcon.icns', 'Applications', 'Julia-1.3.app']
        appname = next(filter(lambda x: x.lower().startswith('julia'),
                              os.listdir(root)))
        src_path = os.path.join(root, appname)
        dest_path = os.path.join(install_dir, appname)
        if os.path.exists(dest_path):
            logging.info(f"remove previous {dest_path}")
            shutil.rmtree(dest_path)
        shutil.copytree(src_path, dest_path)
    bin_path = os.path.join(dest_path,
                            "Contents", "Resources", "julia", "bin", "julia")
    make_symlinks(bin_path, symlink_dir, version)
    return True


def install_julia(version=None, *,
                  install_dir=None,
                  symlink_dir=None,
                  update=False,
                  upstream=None,
                  confirm=False):
    """
    Install julia for Linux and MacOS

    Arguments:
      version: Option examples: 1, 1.2, 1.2.3, latest.
      By default it's the latest stable release. See also `jill update`
      upstream:
        manually choose a download upstream. For example, set it to "Official"
        if you want to download from JuliaComputing's s3 buckets.
      update: add `--update` to update release info before downloading.
      confirm: add `--confirm` to skip interactive prompt.
    """
    install_dir = install_dir if install_dir else default_install_dir()
    symlink_dir = symlink_dir if symlink_dir else default_symlink_dir()
    system, arch = current_system(), current_architecture()
    version = str(version) if version else ''
    version = latest_version(version, system, arch)

    if not confirm:
        question = "jill will:\n"
        question += f"    1) download Julia-{version}-{system}-{arch}"
        question += " into current folder\n"
        question += f"    2) install it into {install_dir}\n"
        question += f"    3) make symlinks in {symlink_dir}\n"
        question += f"    4) add {symlink_dir} to PATH if necessary\n"
        question += "Continue installation?"
        to_continue = query_yes_no(question)
        if not to_continue:
            return False

    overwrite = True if version == "latest" else False
    package_path = download_package(version, system, arch,
                                    upstream=upstream,
                                    update=update,
                                    overwrite=overwrite)
    if not package_path:
        return False

    if system == "macos":
        installer = install_julia_mac
    elif system == "linux":
        installer = install_julia_linux
    else:
        raise ValueError(f"Unsupported system {system}")

    installer(package_path, install_dir, symlink_dir, version)
    return True
