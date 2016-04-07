"""
This scripts builds a list of eggs which are likely to have invalid platform
tag.

THe list is output as a dict that may be merged with the existing platform tag
blacklist in okonomiyaki.file_formats._blacklist
"""
from __future__ import print_function

import collections
import os.path
import pprint
import re
import sys

from okonomiyaki.errors import OkonomiyakiError
from okonomiyaki.file_formats import EggMetadata
from okonomiyaki.utils import compute_sha256

from six import StringIO
from yapf.yapflib.yapf_api import FormatCode

import zipfile2


_IS_BINARY = re.compile("(\.pyd$)|(\.so$)|(\.dylib$)|(\.dll$)|(\.lib$)")


CP27_INVALID_LIST = set((
    "basemap_ld-1.0.1-1",
    "basemap_ld-1.0.2-1",
    "basemap_ld-1.0.6-1",
    "basemap_ld-1.0.7-1",
    "casuarius-1.0-1",
    "casuarius-1.0b1-1",
    "casuarius-1.1-1",
    "casuarius-1.1-2",
    "casuarius-1.1-3",
    "cdecimal-2.3-1",
    "dynd_python-0.6.6-1",
    "dynd_python-0.6.6-2",
    "faulthandler-2.3-1",
    "faulthandler-2.3-2",
    "faulthandler-2.4-1",
    "gmpy-1.11-1",
    "gmpy-1.11-2",
    "gmpy-1.11-3",
    "kiwisolver-0.1.2-1",
    "kiwisolver-0.1.3-1",
    "mistune-0.6-1",
    "mistune-0.6-2",
    "mkl-10.2-1",
    "mkl-10.2-2",
    "mkl-10.3-1",
    "opencv-2.4.5-2",
    "opencv-2.4.5-3",
    "opencv-2.4.5-4",
    "opencv-2.4.5-5",
    "opencv-2.4.9-1",
    "opencv-2.4.9-2",
    "pyaudio-0.2.4-1",
    "pymc-2.1b0-1",
    "pyodbc-2.1.8-1",
    "pyodbc-3.0.10-1",
    "pyodbc-3.0.6-1",
    "pyodbc-3.0.7-1",
    "pyodbc-3.0.7-2",
    "pyqt-4.10.3-1",
    "pyqt-4.11.0-1",
    "pyqt-4.11.3-1",
    "pyqt-4.11.4-1",
    "pyqt-4.11.4-2",
    "pyqt-4.11.4-3",
    "pyside-1.0.0b3-1",
    "pyside-1.0.0b5-1",
    "pyside-1.0.0rc1-1",
    "pyside-1.0.2-1",
    "pyside-1.0.3-1",
    "pyside-1.0.3-2",
    "pyside-1.0.5-1",
    "pyside-1.0.7-1",
    "pyside-1.0.8-1",
    "pyside-1.0.8-2",
    "pyside-1.0.9-1",
    "pyside-1.1.0-1",
    "pyside-1.1.0-2",
    "pyside-1.1.0-3",
    "pyside-1.2.1-1",
    "pyside-1.2.1-2",
    "pyside-1.2.2-1",
    "pyside-1.2.2-2",
    "shiboken-1.2.1-1",
    "shiboken-1.2.1-2",
    "shiboken-1.2.1-3",
    "shiboken-1.2.2-1",
    "shiboken-1.2.2-2",
    "shiboken-1.2.2-3",
    "sip-4.15.3-1",
    "sip-4.16.1-1",
    "sip-4.16.7-1",
    "ujson-1.33.0-1",
    "ujson-1.33.0-2",
    "ujson-1.35-1",
))

PY27_INVALID_LIST = set((
    "agw-0.9.1-1",
    "doclinks-7.1-1",
    "doclinks-7.1-2",
    "doclinks-7.2-1",
    "doclinks-7.2-2",
    "doclinks-7.3-1",
    "enstaller-4.5.0-1",
    "enstaller-4.5.1-1",
    "enstaller-4.5.2-1",
    "enstaller-4.5.3-1",
    "epddocs-1.0-1",
    "epdindex-1.0-1",
    "epdindex-1.1-1",
    "epdindex-1.2-1",
    "examples-7.1-1",
    "examples-7.1-2",
    "examples-7.2-1",
    "examples-7.3-1",
    "iris-1.7.3-1",
    "iris-1.7.3-10",
    "iris-1.7.3-2",
    "iris-1.7.3-3",
    "iris-1.7.3-4",
    "iris-1.7.3-5",
    "iris-1.7.3-6",
    "iris-1.7.3-7",
    "iris-1.7.3-8",
    "iris-1.7.3-9",
    "pythondoc-2.7.3-1",
    "scite-1.74-3",
    "scite-1.74-4",
    "scite-1.74-6",
))


def _get_name(zp, metadata):
    if metadata.python is None:
        for name in zp.namelist():
            if not name.startswith("EGG-INFO"):
                m = _IS_BINARY.search(name)
                if m:
                    return name
    return None


def may_be_invalid(path):
    principal = os.path.splitext(os.path.basename(path))[0].lower()

    with zipfile2.ZipFile(path) as zp:
        metadata = EggMetadata.from_egg(zp)

        name = _get_name(zp, metadata)
        if name is not None:
            print(
                "CP27 {} (because of {})".format(path, name),
                file=sys.stderr
            )
            return "cp27"
        elif principal in PY27_INVALID_LIST:
            if metadata.python is None:
                print("PY27 {}".format(path), file=sys.stderr)
                return "py27"
        elif principal in CP27_INVALID_LIST:
            if metadata.python is None:
                print("CP27 {}".format(path), file=sys.stderr)
                return "cp27"
        return None


def build_list(top):
    ret = collections.defaultdict(dict)

    for root, dirs, files in os.walk(top):
        print(root, file=sys.stderr)
        for i, f in enumerate(files):
            if i % 100 == 0:
                print("{}/{}".format(i, len(files)), end="\r", file=sys.stderr)
                sys.stderr.flush()
            if f.endswith(".egg"):
                path = os.path.normpath(os.path.abspath(os.path.join(root, f)))
                try:
                    python_tag = may_be_invalid(path)
                    if python_tag is not None:
                        key = os.path.basename(path)
                        sha256 = compute_sha256(path)
                        ret[key][sha256] = python_tag
                except OkonomiyakiError as e:
                    msg = "Okonomiyaki error parsing {!r} ({!r})"
                    print(msg.format(path, str(e)), file=sys.stderr)
                except Exception as e:
                    msg = "Okonomiyaki bug parsing {!r} ({!r})"
                    print(msg.format(path, str(e)), file=sys.stderr)
    return dict(ret)


if __name__ == "__main__":
    top = sys.argv[1]

    buf = StringIO()
    pprint.pprint(build_list(top), buf)

    output, ignored = FormatCode(buf.getvalue())
    print("")
    print(output)
