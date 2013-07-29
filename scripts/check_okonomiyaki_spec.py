"""
Small script to check there is no discrepency between our info_from_z and
the one from egginst.

It compares both implementations on every egg we in our repo.
"""
import glob
import os
import zipfile

import os.path as op

from egginst import eggmeta
from okonomiyaki.models.common import info_from_z

PREFIX = "/export/repo/epd/eggs"
ARCNAME = op.join("EGG-INFO/spec/depend")

for d in ["Windows/x86", "Windows/amd64", "RedHat/RH5_x86", "RedHat/RH5_amd64",
          "RedHat/RH3_x86", "RedHat/RH3_amd64", "MacOSX/x86", "MacOSX/amd64"]:
    print d
    for egg in glob.glob(op.join(PREFIX, d, "*egg")):
        with zipfile.ZipFile(egg, "r") as fp:
            r_spec = eggmeta.info_from_z(fp)
            spec = info_from_z(fp)

            if  r_spec != spec:
                print egg
