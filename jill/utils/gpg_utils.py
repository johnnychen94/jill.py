from .defaults import GPG_PUBLIC_KEY_PATH

from gnupg import GPG
from tempfile import TemporaryDirectory


def _verify_gpg(gpg: GPG, datafile, signature_file):
    # this requires gnupg installed in the system
    with open(signature_file, "rb") as fh:
        return gpg.verify_file(fh, data_filename=datafile)


def verify_gpg(datafile, signature_file=None) -> bool:
    """
    verify Julia releases using GPG
    """
    if signature_file is None:
        signature_file = datafile + ".asc"

    with open(GPG_PUBLIC_KEY_PATH) as fh:
        keycontent = fh.read()

    rst = False
    try:
        with TemporaryDirectory() as tmpdir:
            gpg = GPG(gnupghome=tmpdir)
            gpg.import_keys(keycontent)
            rst = bool(_verify_gpg(gpg, datafile, signature_file))
    except FileNotFoundError:
        # issue #45 -- might reaches here during the temp dir cleanup
        # This might only related to VM environment
        # https://bugs.python.org/issue25717
        pass
    finally:
        return rst
