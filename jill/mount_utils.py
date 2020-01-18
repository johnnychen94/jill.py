import os
import sys
import subprocess
import shutil
from tempfile import mkdtemp


class Mounter:
    def __init__(self, src_path, mount_root="."):
        self.src_path = src_path
        self.mount_root = os.path.abspath(mount_root)
        mount_name = os.path.splitext(os.path.split(self.src_path)[1])[0]
        self.mount_point = os.path.join(self.mount_root, mount_name)


class TarMounter(Mounter):
    def __enter__(self):
        self.tempdir = mkdtemp()
        # TODO: support .tar
        args = ["tar", "-zxf", self.src_path, "-C", self.tempdir]
        extra_args = ["--strip-components", "1"]

        args.extend(extra_args)
        is_success = subprocess.run(args).returncode == 0
        return self.tempdir

    def __exit__(self, type, value, tb):
        shutil.rmtree(self.tempdir)


class DmgMounter(Mounter):
    def __init__(self, src_path, mount_root=".", verbose=False, max_try=5):
        super(DmgMounter, self).__init__(src_path, mount_root)
        self.extra_args = ["-mount", "required"]
        self.max_try = max_try
        if not verbose:
            self.extra_args.append("-quiet")

    @staticmethod
    def umount(mount_point):
        if os.path.exists(mount_point):
            rst = subprocess.run(["umount", mount_point])
            return not rst.returncode
        return True

    def __enter__(self):
        assert sys.platform == "darwin"
        args = ["hdiutil", "attach", self.src_path,
                "-mountpoint", self.mount_point]
        args.extend(self.extra_args)
        DmgMounter.umount(self.mount_point)

        # the mount might fail for unknown reason,
        # set a max_try here to work it around
        cur_try = 1
        while cur_try <= self.max_try:
            is_success = subprocess.run(args).returncode == 0
            if is_success:
                return self.mount_point
            time.sleep(0.5)
            cur_try += 1

        raise IOError(f"{self.src_path} is not mounted successfully")

    def __exit__(self, type, value, tb):
        DmgMounter.umount(self.mount_point)
