# Overview

This repository shows three ways to set up [spm-python](https://github.com/spm/spm-python) on Linux and Windows. Two ways use a Python environment: either a venv with pip or a conda environment. The third approach uses a container image for Podman or Docker.

The main focus is the environment-based setup, which does not need root access. First we do some initial prep, then install spm-python and lastly illustrate how to use it in JupyterLab. We also note additional requirements for headless setups and testing.

All steps were tested on x86-64 systems running Linux and Windows, since MathWorks provides the MATLAB Runtime for ARM64 only on macOS. The conda and venv setups can work on those Apple silicon Macs, but see the caveats in the [matlab-runtime README](https://github.com/balbasty/matlab-runtime#readme).

# Installation: Environment-based

Both venv and conda based approaches install MATLAB Runtime R2025b, which spm-python needs to run the standalone version of SPM. spm-python with R2025b supports Python 3.10 to 3.13. The runtime download is 5 GB, which expands to an installed runtime that takes up 11 GB. The installer also needs another 11 GB of temporary space while it runs.

Each setup path below is self-contained, the general steps are:

1. Open a terminal and clone this repository.
2. Set two environment variables for this terminal session: `TMPDIR` and `MATLAB_RUNTIME_PATH`.
3. Create the Python environment with conda or venv.
4. Store the runtime variables in the environment, so that each activation sets them.
5. Install the MATLAB Runtime.
6. Run SPM from Python to check the installation.
7. Clean up the temporary files.
8. Run the demo script from the command line.
9. Start JupyterLab with the demo notebook.

Conda is convenient as it does not need administrator rights, is usually available on HPCs, and stores the runtime variables in the environment itself. In addition to `venv`, `uv` may also be used here.

The two environment variables are:
- `TMPDIR` points to the folder for temporary files. It must be located on disk, because `/tmp` on Debian 13 (and Ubuntu 26.04) is in memory and usually too small for the installer. The variable `TMPDIR` as well as the folder it's pointing at should not persist once installation is done and both will be removed in step 7.
- `MATLAB_RUNTIME_PATH` points to the folder that will contain `R2025b` and is required for both installation as well as later during runtime and hence needs to persist. It is currently located inside this repository but any other folder can be chosen for the runtime, as well as tmp and later, venv.

<details>
<summary>Linux with conda</summary>

0. For this setup, make sure that `conda` or `mamba` is available, for example from [Miniforge](https://github.com/conda-forge/miniforge). The following steps use `conda`, but you can equivalently use `mamba` instead.

1. Open a terminal and clone this repository:

   ```bash
   git clone https://github.com/pranaysy/spm-python-setup.git
   cd spm-python-setup
   ```

2. Set the two environment variables for this terminal session:

   ```bash
   export TMPDIR="$PWD/tmp"
   export MATLAB_RUNTIME_PATH="$PWD/MATLABRuntime"
   mkdir -p "$TMPDIR"
   ```

3. Create the environment `spm` from [`environment.yml`](environment.yml):

   ```bash
   conda env create -f environment.yml
   ```

4. Store the runtime variables in the environment. conda sets them on each `conda activate spm`. `LD_LIBRARY_PATH` lets the runtime find its own libraries for figures.

   ```bash
   conda env config vars set -n spm \
       MATLAB_RUNTIME_PATH="$MATLAB_RUNTIME_PATH" \
       LD_LIBRARY_PATH="$MATLAB_RUNTIME_PATH/R2025b/bin/glnxa64"
   ```

5. Install the MATLAB Runtime into `MATLAB_RUNTIME_PATH`. The `--yes` option accepts the MATLAB Runtime licence.

   ```bash
   conda activate spm
   install_matlab_runtime --version R2025b --prefix "$MATLAB_RUNTIME_PATH" --yes
   ```

6. Run SPM from Python:

   ```bash
   python -c "import spm; print(spm.spm('Version'))"
   ```

   The output is `SPM25 (25.01.02)`. The first call to spm in each Python process starts the MATLAB Runtime, which takes a few seconds.

7. If step 6 succeeded, clean up: unset `TMPDIR` and remove the folder `tmp`.

   ```bash
   unset TMPDIR
   rm -rf tmp
   ```

8. Run the demo script [`notebooks/demo.py`](notebooks/demo.py) from the command line:

   ```bash
   python notebooks/demo.py
   ```

   It prints the SPM version, opens the canonical T1 image in the SPM window, and saves that window to `notebooks/t1_script_001.png`. The SPM window closes when the script ends.

9. Start JupyterLab with the demo notebook [`notebooks/demo.ipynb`](notebooks/demo.ipynb):

   ```bash
   jupyter lab notebooks/demo.ipynb
   ```

</details>

<details>
<summary>Linux with venv</summary>

0. Python is available system-wide by default on Debian and its derivatives such as Ubuntu and Linux Mint. Just one additional system package, `python3-venv`, is necessary but requires root access and can be installed with:

   ```bash
   sudo apt install python3-venv
   ```

   Depending on your system, this may end up installing additional packages. If sudo privileges are not available, use the conda-based setup above, or a package manager like [`uv`](https://docs.astral.sh/uv) (not covered here) for fully user-managed environments.

1. Open a terminal and clone this repository:

   ```bash
   git clone https://github.com/pranaysy/spm-python-setup.git
   cd spm-python-setup
   ```

2. Set the two environment variables for this terminal session:

   ```bash
   export TMPDIR="$PWD/tmp"
   export MATLAB_RUNTIME_PATH="$PWD/MATLABRuntime"
   mkdir -p "$TMPDIR"
   ```

3. Create the environment `spm-venv` from [`requirements.txt`](requirements.txt):

   ```bash
   python3 -m venv spm-venv
   spm-venv/bin/pip install -r requirements.txt
   ```

4. Print the full path of the runtime folder:

   ```bash
   echo "$MATLAB_RUNTIME_PATH"
   ```

   Then open `spm-venv/bin/activate` in a text editor and add the following two lines at the end. Replace `/path/to/spm-python-setup/MATLABRuntime` with the path that `echo` printed. `LD_LIBRARY_PATH` lets the runtime find its own libraries for figures.

   ```bash
   export MATLAB_RUNTIME_PATH="/path/to/spm-python-setup/MATLABRuntime"
   export LD_LIBRARY_PATH="$MATLAB_RUNTIME_PATH/R2025b/bin/glnxa64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
   ```

5. Activate the newly created environment and install the MATLAB Runtime into `MATLAB_RUNTIME_PATH`. The `--yes` option accepts the MATLAB Runtime licence.

   ```bash
   . spm-venv/bin/activate
   install_matlab_runtime --version R2025b --prefix "$MATLAB_RUNTIME_PATH" --yes
   ```

6. Run SPM from Python:

   ```bash
   python -c "import spm; print(spm.spm('Version'))"
   ```

   The output is `SPM25 (25.01.02)`. The first call to spm in each Python process starts the MATLAB Runtime, which takes a few seconds.

7. If step 6 succeeded, clean up: unset `TMPDIR` and remove the folder `tmp`.

   ```bash
   unset TMPDIR
   rm -rf tmp
   ```

8. Run the demo script [`notebooks/demo.py`](notebooks/demo.py) from the command line:

   ```bash
   python notebooks/demo.py
   ```

   It prints the SPM version, opens the canonical T1 image in the SPM window, and saves that window to `notebooks/t1_script_001.png`. The SPM window closes when the script ends.

9. Start JupyterLab with the demo notebook [`notebooks/demo.ipynb`](notebooks/demo.ipynb):

   ```bash
   jupyter lab notebooks/demo.ipynb
   ```

</details>

<details>
<summary>Windows with conda</summary>

0. Make sure that conda is available, for example from [Miniforge](https://github.com/conda-forge/miniforge). Run all steps in the Miniforge Prompt. If `git` is not available, download this repository as a ZIP file from GitHub, unpack it, and go to its folder instead of step 1.

1. Open the Miniforge Prompt and clone this repository:

   ```bat
   git clone https://github.com/pranaysy/spm-python-setup.git
   cd spm-python-setup
   ```

2. Set the two environment variables for this terminal session:

   ```bat
   set TMPDIR=%CD%\tmp
   set MATLAB_RUNTIME_PATH=%CD%\MATLABRuntime
   mkdir "%TMPDIR%"
   ```

3. Create the environment `spm` from [`environment.yml`](environment.yml):

   ```bat
   conda env create -f environment.yml
   ```

4. Store the runtime variable in the environment. conda sets it on each `conda activate spm`.

   ```bat
   conda env config vars set -n spm MATLAB_RUNTIME_PATH="%MATLAB_RUNTIME_PATH%"
   ```

5. Install the MATLAB Runtime into `MATLAB_RUNTIME_PATH`. The `--yes` option accepts the MATLAB Runtime licence.

   ```bat
   conda activate spm
   set __COMPAT_LAYER=RunAsInvoker
   install_matlab_runtime --version R2025b --prefix "%MATLAB_RUNTIME_PATH%" --yes
   set __COMPAT_LAYER=
   ```

   On Windows, the runtime installer asks for administrator rights. `__COMPAT_LAYER=RunAsInvoker` makes Windows run it with your own rights instead. If the install still fails, start the Miniforge Prompt as administrator, go to this repository folder, set the two variables again, and repeat this step.

6. Run SPM from Python:

   ```bat
   python -c "import spm; print(spm.spm('Version'))"
   ```

   The output is `SPM25 (25.01.02)`. The first call to spm in each Python process starts the MATLAB Runtime, which takes a few seconds.

7. If step 6 succeeded, clean up: unset `TMPDIR` and remove the folder `tmp`.

   ```bat
   set TMPDIR=
   rmdir /s /q tmp
   ```

8. Run the demo script [`notebooks/demo.py`](notebooks/demo.py) from the command line:

   ```bat
   python notebooks\demo.py
   ```

   It prints the SPM version, opens the canonical T1 image in the SPM window, and saves that window to `notebooks/t1_script_001.png`. The SPM window closes when the script ends.

9. Start JupyterLab with the demo notebook [`notebooks/demo.ipynb`](notebooks/demo.ipynb):

   ```bat
   jupyter lab notebooks/demo.ipynb
   ```

</details>

<details>
<summary>Windows with venv</summary>

0. Install Python 3.13 from [python.org](https://www.python.org/downloads/windows/), or with the [Python install manager](https://docs.python.org/3/using/windows.html) by running `py install 3.13`. spm-python supports Python 3.10 to 3.13. Once installed, run all steps in one Command Prompt (cmd). If `git` is not available, download this repository as a ZIP file from GitHub, unpack it, and go to its folder instead of step 1.

1. Open a Command Prompt and clone this repository:

   ```bat
   git clone https://github.com/pranaysy/spm-python-setup.git
   cd spm-python-setup
   ```

2. Set the two environment variables for this terminal session:

   ```bat
   set TMPDIR=%CD%\tmp
   set MATLAB_RUNTIME_PATH=%CD%\MATLABRuntime
   mkdir "%TMPDIR%"
   ```

3. Create the environment `spm-venv` from [`requirements.txt`](requirements.txt):

   ```bat
   py -3.13 -m venv spm-venv
   spm-venv\Scripts\python -m pip install -r requirements.txt
   ```

4. Print the full path of the runtime folder:

   ```bat
   echo %MATLAB_RUNTIME_PATH%
   ```

   Then open `spm-venv\Scripts\activate.bat` in a text editor, for example with `notepad spm-venv\Scripts\activate.bat`, and add this line at the end. Replace `C:\path\to\spm-python-setup\MATLABRuntime` with the path that `echo` printed.

   ```bat
   set "MATLAB_RUNTIME_PATH=C:\path\to\spm-python-setup\MATLABRuntime"
   ```

5. Install the MATLAB Runtime into `MATLAB_RUNTIME_PATH`. The `--yes` option accepts the MATLAB Runtime licence.

   ```bat
   spm-venv\Scripts\activate.bat
   set __COMPAT_LAYER=RunAsInvoker
   install_matlab_runtime --version R2025b --prefix "%MATLAB_RUNTIME_PATH%" --yes
   set __COMPAT_LAYER=
   ```

   On Windows, the runtime installer asks for administrator rights. `__COMPAT_LAYER=RunAsInvoker` makes Windows run it with your own rights instead. If the install still fails, start the Command Prompt as administrator, go to this repository folder, set the two variables again, and repeat this step.

6. Run SPM from Python:

   ```bat
   python -c "import spm; print(spm.spm('Version'))"
   ```

   The output is `SPM25 (25.01.02)`. The first call to spm in each Python process starts the MATLAB Runtime, which takes a few seconds.

7. If step 6 succeeded, clean up: unset `TMPDIR` and remove the folder `tmp`.

   ```bat
   set TMPDIR=
   rmdir /s /q tmp
   ```

8. Run the demo script [`notebooks/demo.py`](notebooks/demo.py) from the command line:

   ```bat
   python notebooks\demo.py
   ```

   It prints the SPM version, opens the canonical T1 image in the SPM window, and saves that window to `notebooks/t1_script_001.png`. The SPM window closes when the script ends.

9. Start JupyterLab with the demo notebook [`notebooks/demo.ipynb`](notebooks/demo.ipynb):

   ```bat
   jupyter lab notebooks/demo.ipynb
   ```

</details>

## Headless installations

The steps above are for a desktop installation with a graphical environment, which already has the system packages needed by the MATLAB Runtime. A minimal server installation likely won't have them, and an administrator or a user with sudo privileges can install them system-wide once:

```bash
sudo apt install \
    libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 libatspi2.0-0t64 \
    libcups2t64 libdrm2 libgbm1 libgl1 libice6 libnspr4 libnss3 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libxt6t64
```

To create or print figures without a display, also install these packages:

```bash
sudo apt install libfontconfig1 libgdk-pixbuf-2.0-0 xvfb xauth
```

Then run Python through `xvfb-run` inside a venv/conda environment with spm-python, which gives it a virtual display for rendering figures:

```bash
conda activate spm
xvfb-run -a python notebooks/demo.py
```

If no display is set and `libxfont2`, `libtirpc3t64`, `xkb-data` and `x11-xkb-utils` are installed, the MATLAB Runtime starts its own virtual display.

This list of packages is not exhaustive and was tested on a headless Debian 13 host with the runtime products that SPM uses. Other systems or other uses of the runtime may need more packages.

# Installation: Container-based

The container image has spm-python, JupyterLab and the parts of the MATLAB Runtime R2025b that SPM uses, on Debian 13. These steps are for a Linux host with podman, which runs rootless by default, or with rootless Docker ([setup guide](https://docs.docker.com/engine/security/rootless/)). The image takes up 3.2 GB, and the download is about 1 GB. The image contains the MATLAB Runtime. If you use the image, you accept the [MATLAB Runtime licence](https://www.mathworks.com/products/compiler/matlab-runtime.html).

The image is for x86-64 (`linux/amd64`) only. On ARM64 hosts, it can run only through emulation, which is not officially supported. Podman is preferable over Docker as it runs rootless out of the box, avoids a persistent privileged daemon and `--userns=keep-id` makes it convenient to map uids for writing files.

1. Clone this repository and get the image:

   ```bash
   git clone https://github.com/pranaysy/spm-python-setup.git
   cd spm-python-setup
   podman pull ghcr.io/pranaysy/spm-python-setup      # podman
   docker pull ghcr.io/pranaysy/spm-python-setup      # or Docker
   ```

2. Let containers use your system's display, run this once in each desktop session:

   ```bash
   xhost +local:
   ```

3. Start JupyterLab with the demo notebook. The working directory used by JupyterLab inside the container is `/work` and the following command mounts the folder `notebooks` of this repository at `/work/notebooks` inside the container:

   podman:

   ```bash
   podman run --rm --interactive --tty --userns=keep-id:uid=1000,gid=1000 \
       --env DISPLAY --volume /tmp/.X11-unix:/tmp/.X11-unix \
       --publish 127.0.0.1:8888:8888 \
       --volume "$PWD/notebooks":/work/notebooks \
       --workdir /work \
       ghcr.io/pranaysy/spm-python-setup jupyter lab --ip=0.0.0.0 --no-browser
   ```

   With `--userns=keep-id:uid=1000,gid=1000`, the files that the container writes in `notebooks` belong to the user running the container i.e. you. The option maps your user, whatever its uid, to the user `spm` (uid 1000) inside the container.

   Docker:

   ```bash
   # chmod a+rwx notebooks    # for rootless
   docker run --rm --interactive --tty \
       --env DISPLAY --volume /tmp/.X11-unix:/tmp/.X11-unix \
       --publish 127.0.0.1:8888:8888 \
       --volume "$PWD/notebooks":/work/notebooks \
       --workdir /work \
       ghcr.io/pranaysy/spm-python-setup jupyter lab --ip=0.0.0.0 --no-browser
   ```

   With Docker, the container runs as a user with uid 1000. But when using rootless Docker, or if your uid is not 1000, this user cannot write in your folders, so that folder should be made writable first.

   JupyterLab prints a link that starts with `http://127.0.0.1:8888/lab?token=`. Open that link in your browser, then open `notebooks/demo.ipynb` in the file browser of JupyterLab. To stop JupyterLab, press Ctrl+C.

   JupyterLab's working directory is set to `/work` using the flag `--workdir`, and `notebooks` is mounted under it. Any additional folders containing data or scripts should also be mounted as subfolders of `/work`, for example `--volume "$PWD/data":/work/data --volume "$PWD/scripts":/work/scripts`. Again, with Docker, these folders should be writable.

   If you leave out the `--volume` and `--workdir` options for your folders, JupyterLab launches from `/home/spm` inside the container. Notebooks saved there will not persist when the container stops.

4. To run a script without JupyterLab, add `python` and the script after the image name. These examples run the demo script `notebooks/demo.py` without a display, for example on a server. The MATLAB Runtime then draws the figure on its own virtual display inside the container, and the script saves it to `notebooks/t1_script_001.png`. With Docker, the folder must be writable, as in step 3.

   podman:

   ```bash
   podman run --rm --userns=keep-id:uid=1000,gid=1000 \
       --volume "$PWD/notebooks":/work/notebooks \
       --workdir /work \
       ghcr.io/pranaysy/spm-python-setup python notebooks/demo.py
   ```

   Docker:

   ```bash
   docker run --rm \
       --volume "$PWD/notebooks":/work/notebooks \
       --workdir /work \
       ghcr.io/pranaysy/spm-python-setup python notebooks/demo.py
   ```

## Building the OCI image
To build the image yourself, run one of these commands from the root of this repository. The build downloads 5 GB from MathWorks and accepts the MATLAB Runtime licence for you.

The image does not contain the full MATLAB Runtime (11 GB). [`install_runtime_products.py`](install_runtime_products.py) installs only the five products that the compiled SPM package lists as required, 2.6 GB in total:

- MATLAB Base Runtime
- MATLAB Standard Runtime Addon
- MATLAB Extended Runtime Addon
- MATLAB Graphics Runtime Addon
- Python Target Runtime Addon

The build also leaves out files that the image does not use: the graphics drivers of Mesa and LLVM, because the runtime draws figures with its own software renderer. The test suites of the Python packages in the venv are also removed.

```bash
podman build --file Containerfile --tag ghcr.io/pranaysy/spm-python-setup .
docker build --file Containerfile --tag ghcr.io/pranaysy/spm-python-setup .
```

## Troubleshooting rootful Docker

With rootful Docker, the first call to spm can stop with this error:

```
library initialization failed - unable to allocate file descriptor table - out of memory
```

MATLAB Runtime R2025b contains Java 8, which on launch, reserves a table with one entry for each file that the process is allowed to open. The size of this table is governed by a hard limit for open files, and some rootful Docker installations set that limit to more than one billion per container. For example, the `containerd` service on Debian 13 sets `LimitNOFILE=infinity`. The table then needs about 50 GB of memory, which cannot be reserved by Java and hence it stops with the error above. Java fixed this upstream in [JDK-8150460](https://bugs.openjdk.org/browse/JDK-8150460) (Java 9, backported to Java 8 update 252), but MATLAB Runtime R2025b still contains the older Java 8 update 202. Rootless Docker and podman use the limit of your user session, usually 524288, which gives a table of about 25 MB.

To fix the error, add `--ulimit nofile=1024:524288` to the `docker run` command. The second number is the hard limit. For example, the command from step 3 becomes:

```bash
docker run --rm --interactive --tty --ulimit nofile=1024:524288 \
    --env DISPLAY --volume /tmp/.X11-unix:/tmp/.X11-unix \
    --publish 127.0.0.1:8888:8888 \
    --volume "$PWD/notebooks":/work/notebooks \
    --workdir /work \
    ghcr.io/pranaysy/spm-python-setup jupyter lab --ip=0.0.0.0 --no-browser
```

# Demos
The `notebooks` folder in this repository contains various jupyter notebooks showing the usage of spm-python.

- `demo.ipynb`: A minimal demo that imports spm-python and opens the canonical T1 image of SPM with `spm_check_registration`.
- `demo.py`: The same demo as a Python script, to run from the command line.

# Testing

spm-python has unit tests in its repository. To run them, get the tests for the spm-python version in `requirements.txt` and `environment.yml` (tag `25.1.2.post2`). Run these commands from the root of this repository:

```bash
git clone --depth 1 --branch 25.1.2.post2 https://github.com/spm/spm-python.git tmp/spm-python
```

## Environment-based

Activate an environment (conda or venv), then run:

```bash
python -m unittest discover -s tmp/spm-python/tests
```

## Container-based

Mount the tests into the container and run them there:

```bash
podman run --rm --volume "$PWD/tmp/spm-python/tests":/tests:ro ghcr.io/pranaysy/spm-python-setup python -m unittest discover -s /tests
docker run --rm --volume "$PWD/tmp/spm-python/tests":/tests:ro ghcr.io/pranaysy/spm-python-setup python -m unittest discover -s /tests
```

The output (hopefully) ends with `Ran 127 tests` and `OK`.
