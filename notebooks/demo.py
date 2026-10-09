"""Minimal spm-python demo as a script.

Prints the SPM version, shows the canonical T1 image of SPM with
spm_check_registration, and saves the SPM Graphics window to
t1_script_001.png next to this script.

    python notebooks/demo.py
"""
import os
from pathlib import Path

# MATLAB keeps the working folder that it starts in, so change to the folder
# of this script before the first spm call. The figure then lands here.
os.chdir(Path(__file__).parent)

import spm  # noqa: E402

print(spm.spm("Version"))

t1 = Path(spm.spm("Dir")) / "canonical" / "single_subj_T1.nii"
spm.spm_check_registration(str(t1))

# spm_print adds a number to the file name: t1_script_001.png on the first run
spm.spm_print("t1_script.png", "Graphics", "png", nargout=0)
