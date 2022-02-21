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


def sorted_display_list(julialist, reverse):
    # We sort the julia paths in the following order for better display:
    #   julia
    #   julia-<major>
    #   julia-<major>.<minor>
    #   julia-<special name>

    # I just get lazy to write this up so 🤷‍♂️ as long as it works I'm happy
    julia = []
    julia_major = []
    julia_major_minor = []
    julia_special = []
    for x in julialist:
        if x == 'julia':
            julia.append(x)
        elif re.match(r"^julia.\d+$", x):
            julia_major.append(x)
        elif re.match(r"^julia.\d+\.\d+$", x):
            julia_major_minor.append(x)
        else:
            julia_special.append(x)
    julia.sort(reverse=reverse)  # this actually only have 1 element.
    julia_major.sort(reverse=reverse)
    julia_major_minor.sort(reverse=reverse)
    julia_special.sort(reverse=reverse)
    return [*julia, *julia_major, *julia_major_minor, *julia_special]


def list_julia(version=None, *,
               symlink_dir=None):
    """
        List all Julia executable versions in symlink dir

    Arguments:
      version: (Optional)
        The specific version prefix that you are interested in. For example, `jill list 1` checks
        every symlink that matches the name pattern `^julia-1`. (`julia` is excluded in this case.)
      symlink_dir: (Optional)
        The symlink dir that `jill list` looks at.
    """
    symlink_dir = symlink_dir if symlink_dir else default_symlink_dir()
    if not os.path.exists(symlink_dir):
        print(
            f"Found 0 julia(s) in {color.UNDERLINE}{symlink_dir}{color.END}:")

    version = str(version) if version else ''
    if version:
        pattern = f"^julia-{version}"
    else:
        pattern = "^julia"
    julias = search_files(symlink_dir, pattern=pattern)
    julias = sorted_display_list(julias, reverse=True)
    version_list = [get_binversion(os.path.join(symlink_dir, x)) for x in julias]  # nopep8

    print(f"Found {len(julias)} julia(s) in {color.UNDERLINE}{symlink_dir}{color.END}:")  # nopep8
    for binname, (binversion, build) in zip(julias, version_list):
        if binname.endswith(".cmd"):
            # hide .cmd ext for Windows
            binname = os.path.splitext(binname)[0]
        build_msg = f"+{build}" if build else ""
        binversion_msg = f"{color.RED}Invalid{color.END}" if binversion == '0.0.1' else binversion
        print(f"{color.BOLD}{binname:12}{color.END}\t-->\t{binversion_msg}{build_msg}")
