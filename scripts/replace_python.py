"""
<script> runtime_path python_exe_path 

Replace python.exe by the given python_exe_path in the give runtime
"""
import os.path
import shutil
import sys

import zipfile2

from okonomiyaki.utils import tempdir


path = sys.argv[1]
replacement = sys.argv[2]

to_replace = "python.exe"


with tempdir() as d:
    with zipfile2.ZipFile(path) as zp:
        zp.extractall(d, preserve_permissions=zipfile2.PERMS_PRESERVE_ALL)
        to_replace_path = os.path.join(d, to_replace)
        os.remove(to_replace_path)
        shutil.copy2(replacement, to_replace_path)

    with zipfile2.ZipFile(path, "w", zipfile2.ZIP_DEFLATED) as zp:
        zp.add_tree(d)
