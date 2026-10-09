"""Install only the MATLAB Runtime products that SPM's compiled package needs.

install_matlab_runtime (from the matlab-runtime package) installs the full
MATLAB Runtime: all 72 products, 11 GB. SPM's compiled package (spm-runtime)
lists the few products it needs in its buildresult.json. This script installs
only those, with MathWorks' own installer: 2.6 GB for R2025b.

Run it with the Python of an environment that has spm-python installed.
Environment variables:
  MATLAB_RUNTIME_PATH              install prefix (required); the runtime
                                   goes to <prefix>/<release>
  TMPDIR                           where the 5 GB zip is downloaded and
                                   unpacked (about 10 GB free space needed)
  AGREE_TO_MATLAB_RUNTIME_LICENSE  "yes" (default) accepts the MATLAB Runtime
                                   licence; the installer stops otherwise
"""

import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import spm_runtime
from matlab_runtime.utils import ZipFileWithExecPerm, guess_installer, url_download


def required_product_ids():
    """Product IDs that SPM's compiled package (CTF) declares as required."""
    ctf = Path(spm_runtime.__file__).parent / "_spm" / "_spm.ctf"
    meta = json.loads(zipfile.ZipFile(ctf).read("fsroot/.META/buildresult.json"))
    deps = meta["RuntimeDependencies"]
    return [d["ID"] for d in deps if d.get("Optional", "no") == "no"]


def download_installer(release, workdir):
    """Download the runtime installer zip for this release and unpack it."""
    url = guess_installer(release)  # same URL as install_matlab_runtime uses
    print("downloading", url, flush=True)
    archive = url_download(url, str(workdir))
    installer = workdir / "installer"
    print("unpacking", archive, flush=True)
    ZipFileWithExecPerm(archive).extractall(installer)  # keeps the executable bits
    return installer


def product_names(installer, ids):
    """Installer names of the products.

    The first line of productdata/<ID>.txt in the installer is "name=<name>".
    """
    names = []
    for pid in ids:
        text = (installer / "productdata" / f"{pid}.txt").read_text()
        names.append(text.splitlines()[0].split("=", 1)[1].strip())
    return names


def main():
    release = spm_runtime.__matlab_release__
    prefix = Path(os.environ["MATLAB_RUNTIME_PATH"])
    agree = os.environ.get("AGREE_TO_MATLAB_RUNTIME_LICENSE", "yes")
    ids = required_product_ids()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        installer = download_installer(release, tmp)
        names = product_names(installer, ids)
        products = ", ".join(f"{n} ({i})" for i, n in zip(ids, names, strict=True))
        print("products:", products, flush=True)

        # MathWorks' input file for a silent install; one "product.<name>" line
        # per product selects what gets installed.
        log = tmp / "install.log"
        inputfile = tmp / "input.txt"
        lines = [
            "mode=silent",
            f"destinationFolder={prefix}",
            f"agreeToLicense={agree}",
            f"outputFile={log}",
        ]
        lines += [f"product.{name}" for name in names]
        inputfile.write_text("\n".join(lines) + "\n")
        work = tmp / "work"
        work.mkdir()
        # The installer can exit with 0 after a failure, so do not trust its
        # exit code: judge success from its log and the installed VersionInfo.xml.
        command = [installer / "install", "-inputFile", inputfile, "-tmpdir", work]
        subprocess.run(command, check=False)

        text = log.read_text() if log.exists() else ""
        installed = (prefix / release / "VersionInfo.xml").exists()
        if "End - Successful" not in text or not installed:
            print(text[-3000:], file=sys.stderr)
            sys.exit("MATLAB Runtime installation failed")
    print("installed", prefix / release)


if __name__ == "__main__":
    main()
