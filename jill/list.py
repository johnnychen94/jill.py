from .utils.defaults import default_symlink_dir
from .utils import color
from .install import get_exec_version

import re
import os
import subprocess


def search_files(dir, pattern):
    files = os.listdir(dir)
    julias = [x for x in files if re.match(pattern, x)]
    return julias


def get_julia_build(path):
    ver_cmd = [path, "--startup=no",
               "-e", "println(VERSION, ',', Base.GIT_VERSION_INFO.commit_short)"]
    try:
        build = subprocess.check_output(ver_cmd).decode("utf-8")
        ver, build = build.lower().split(',')
        return ver.strip(), build.strip()
    except:
        return "", ""


def get_binversion(path):
    binversion = get_exec_version(path)
    if binversion.endswith('dev'):
        binversion, build = get_julia_build(path)
    else:
        # we want quick response and we don't really care the commit version of a stable release
        build = ''
    return binversion, build


def list_julia(*, symlink_dir=None):
    """
        List all Julia executable versions in symlink dir

    Arguments:
      symlink_dir: (Optional)
        The symlink dir that `jill list` looks at.
    """
    symlink_dir = symlink_dir if symlink_dir else default_symlink_dir()
    if not os.path.exists(symlink_dir):
        raise(ValueError(f"symlink dir {symlink_dir} doesn't exist!"))

    julias = sorted(search_files(symlink_dir, pattern='^julia'), reverse=True)  # nopep8
    version_list = [get_binversion(os.path.join(symlink_dir, x)) for x in julias]  # nopep8
    print(f"Found {len(julias)} julia(s) in {color.UNDERLINE}{symlink_dir}{color.END}:")  # nopep8
    for binname, (binversion, build) in zip(julias, version_list):
        build_msg = f"+{build}" if build else ""
        binversion_msg = f"{color.RED}Invalid{color.END}" if binversion == '0.0.1' else binversion
        print(f"{color.BOLD}{binname:12}{color.END}\t-->\t{binversion_msg}{build_msg}")
