import argparse
import collections
import os
import pprint
import sys
import zipfile

from six import StringIO

from yapf.yapflib.yapf_api import FormatCode

from okonomiyaki.file_formats import EggMetadata
from okonomiyaki.utils import compute_sha256


with open("invalid_python_tag_eggs_list.txt", "rt") as fp:
    names = set(line.strip() for line in fp)


def build_list(top):
    ret = collections.defaultdict(dict)

    for root, dirs, files in os.walk(top):
        for f in files:
            principal = os.path.splitext(f)[0].lower()
            if f.endswith(".egg") and principal in names:
                path = os.path.join(root, f)
                try:
                    metadata = EggMetadata.from_egg(path)
                except zipfile.BadZipfile:
                    pass
                else:
                    ret[f][compute_sha256(path)] = "py27"
    return dict(ret)


def main():
    p = argparse.ArgumentParser("Generates dict for python_tag blacklist")
    p.add_argument(
        "root", help="eggs directory to walk into to compute blacklist"
    )

    ns = p.parse_args(sys.argv[1:])

    buf = StringIO()
    pprint.pprint(build_list(ns.root), buf)

    output, ignored = FormatCode(buf.getvalue())
    print(output)


if __name__ == "__main__":
    main()
