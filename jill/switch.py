from .utils.defaults import default_symlink_dir
from .utils import current_system
from .utils import color
from .install import get_exec_version

import os
import shutil
import pathlib
import re


def create_symlink(symlink_path, target_path):
    """
    Make symlink at path `symlink_path` so that it points to `target_path`.
    """
    if current_system() == "winnt":
        os.remove(symlink_path)
        if target_path.endswith(".cmd"):
            shutil.copy(target_path, symlink_path)
        with open(symlink_path, "w") as f:
            # create a cmd file to mimic how we do symlinks in linux
            f.writelines(["@echo off\n", f'"{target_path}" %*'])
    else:
        target_path = str(pathlib.Path(target_path).resolve())
        if os.path.exists(symlink_path):
            os.remove(symlink_path)
        os.symlink(target_path, symlink_path)


def is_symlink(file):
    if current_system() == "winnt":
        return file.endswith("cmd")
    else:
        return os.path.islink(file)


def get_juliafile_from_version(version):
    if version in ["latest", "dev"]:
        return version
    if re.match("^\d+(.\d+)?$", version):  # <major> or <major>.<minor>
        return f"julia-{version}"
    elif re.match("^\d+.\d+.\d+$", version):
        print(f"{color.YELLOW}Patch version is currently ignored.{color.END}")  # nopep8
        version = ".".join(version.split(".")[0:2])
        return f"julia-{version}"
    else:
        return None


def switch_julia_target(version_or_path, target="julia", symlink_dir=None):
    """Switch the Julia target version or path.

    Args:
        version_or_path: Path or version of the new Julia executable
        target: Target name (default: 'julia')
        symlink_dir: Symlink directory
    """
    symlink_dir = symlink_dir if symlink_dir else default_symlink_dir()
    if not os.path.exists(symlink_dir):
        raise (ValueError(f"symlink dir {symlink_dir} doesn't exist."))

    julia_symlink = os.path.join(symlink_dir, target)
    if current_system() == "winnt":
        # We use ".cmd" file to mimic symlink in windows.
        # https://github.com/johnnychen94/jill.py/issues/98
        julia_symlink = julia_symlink + ".cmd"
    if not os.path.exists(julia_symlink):
        print(f"{color.RED}{julia_symlink} doesn't exist.{color.END}")
        return False
    if not is_symlink(julia_symlink):
        print(
            f"{color.RED}Found a suspicious situation: the current {julia_symlink} is not a symlink.{color.END}"
        )
        return False

    version_or_path = str(version_or_path)
    if os.path.exists(version_or_path):
        target_julia = version_or_path
    else:
        version = version_or_path
        if version == "1.1":
            msg = f"The fire argparser recognizes the input as jill switch {version_or_path}. This can be either 1.1 or 1.10\n"
            msg += "JILL interprets it as 1.10 and I believe you're not going to use Julia 1.1 as default julia anymore\n"
            print(f"{color.GREEN}{msg}{color.END}")
            version = "1.10"

        target_filename = get_juliafile_from_version(version)
        if not target_filename:
            print(f"{color.RED}Unrecognized input {version}{color.END}")
            return False

        if current_system() == "winnt":
            # JILL uses .cmd to simulate simlinks
            target_filename += ".cmd"
        target_julia = os.path.join(symlink_dir, target_filename)
    if not os.path.exists(target_julia):
        print(f"{color.RED}Target {target_julia} doesn't exist.{color.END}")
        return False

    cur_version = get_exec_version(julia_symlink)
    cur_version = (
        f"{color.YELLOW}Invalid{color.END}" if cur_version == "0.0.1" else cur_version
    )
    target_version = get_exec_version(target_julia)
    if target_version == "0.0.1":
        print(f"{color.RED}Target file {target_julia} is invalid.{color.END}")  # nopep8
        return False

    create_symlink(julia_symlink, target_julia)
    print(
        f"The {color.UNDERLINE}{target}{color.END} target has been changed from {color.UNDERLINE}{cur_version}{color.END} to {color.UNDERLINE}{target_version}{color.END}"
    )  # nopep8
    return True
