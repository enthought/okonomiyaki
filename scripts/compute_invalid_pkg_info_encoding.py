"""
This scripts builds a list of eggs which are likely to have invalid platform
tag.

THe list is output as a dict that may be merged with the existing platform tag
blacklist in okonomiyaki.file_formats._blacklist
"""
from __future__ import print_function

import codecs
import collections
import os.path
import pprint
import subprocess
import sys
import tempfile

import zipfile2

import bag.more_codecs  # noqa

from io import StringIO

from yapf.yapflib.yapf_api import FormatCode


from okonomiyaki.errors import OkonomiyakiError
from okonomiyaki.file_formats import EggMetadata
from okonomiyaki.utils import compute_sha256


ALTERNATIVE_ENCODING = {
    "medialog.boardfile-1.3.2-1.egg": "macintosh",
    "medialog.boardfile-1.6.1-1.egg": "macintosh",
    "medialog.popupworkflow-0.6-1.egg": "macintosh",
    "medialog.subskins-4.1b1-1.egg": "macintosh",
}


def iter_invalid_unicode(top):
    for root, dirs, files in os.walk(top):
        print(root, file=sys.stderr)
        nfiles = len(files)
        for i, f in enumerate(files):
            if i % 100 == 0:
                print("{}/{}".format(i, nfiles), end="\r", file=sys.stderr)
                sys.stderr.flush()
            if f.endswith(".egg"):
                path = os.path.normpath(os.path.abspath(os.path.join(root, f)))
                try:
                    EggMetadata.from_egg(path)
                except OkonomiyakiError as e:
                    msg = "Okonomiyaki error parsing {!r} ({!r})"
                    print(msg.format(path, str(e)), file=sys.stderr)
                except UnicodeDecodeError:
                    yield path


def print_python_code(top, validate_with_vim=False):
    # The dict containing the blacklist
    pkg_infos = {}
    non_ascii_characters = {}

    egg_to_pkg_info = collections.defaultdict(dict)

    for path in iter_invalid_unicode(top):
        print(path)
        filename = os.path.basename(path)

        with zipfile2.ZipFile(path) as fp:
            data = fp.read("EGG-INFO/PKG-INFO")

        sha256 = compute_sha256(path)

        name, version, build = filename.split("-", 2)

        varname = "{}_{}".format(
            name.replace(".", "_").upper(), version.replace(".", "_").upper()
        )
        egg_to_pkg_info[filename][sha256] = varname

        encoding = ALTERNATIVE_ENCODING.get(filename, "latin1")

        content = data.decode(encoding)

        if validate_with_vim:
            candidates = [
                i for i, v in enumerate(content) if ord(v) >= 128
            ]

            non_ascii_characters[varname] = candidates
            for pos in candidates:
                with tempfile.NamedTemporaryFile() as fp:
                    fp.write(content.encode("utf8"))
                    fp.flush()
                    cmd = ["vim", "+normal {}go".format(pos), fp.name]
                    print(path)
                    p = subprocess.Popen(cmd)
                    p.communicate()

        pkg_info = u"\n".join(
            (
                u'\n{} = u"""'.format(varname),
                content,
                u'"""\n',
            )
        )
        pkg_infos[varname] = pkg_info

    py_content = [pkg_infos[k] for k in sorted(pkg_infos)]

    buf = StringIO()
    pprint.pprint(dict(egg_to_pkg_info), buf)

    output, ignored = FormatCode(buf.getvalue())

    py_content.append(output)

    output = u"\n".join(py_content)

    with codecs.open("invalid_unicode.py", "wt", encoding="utf8") as fp:
        fp.write(output)


if __name__ == "__main__":
    top = sys.argv[1]

    print_python_code(top)
