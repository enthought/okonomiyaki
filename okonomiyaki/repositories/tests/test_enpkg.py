import json
import os
import unittest

import os.path as op

from ..enpkg import EnpkgS3IndexEntry
from ...utils import py3compat

DATA_DIR = op.join(op.dirname(__file__), "data")

__st = os.stat(op.join(DATA_DIR, "ets-4.3.0-3.egg"))
ETS_MTIME = __st.st_mtime
ETS_SIZE = __st.st_size

__st = os.stat(op.join(DATA_DIR, "Cython-0.19.1-1.egg"))
CYTHON_MTIME = __st.st_mtime
CYTHON_SIZE = __st.st_size


class TestEnpkgS3IndexEntry(unittest.TestCase):
    def test_from_egg(self):
        path = op.join(DATA_DIR, "ets-4.3.0-3.egg")

        index_entry = EnpkgS3IndexEntry.from_egg(path)
        self.assertEqual(index_entry.build, 3)
        self.assertEqual(index_entry.name, "ets")
        self.assertEqual(index_entry.version, "4.3.0")

    def test_to_json(self):
        r_data = dict(
            available=False,
            build=py3compat.long(3),
            md5=py3compat.u("78ce2b9ebc88e3ed81cb9c0aa4eb8c87"),
            mtime=ETS_MTIME,
            egg_basename=py3compat.u('ets'),
            name=py3compat.u('ets'),
            packages=[
                'apptools 4.2.0-2',
                'blockcanvas 4.0.3-1',
                'casuarius 1.1-1',
                'chaco 4.3.0-2',
                'codetools 4.1.0-2',
                'enable 4.3.0-5',
                'enaml 0.6.8-2',
                'encore 0.3-1',
                'envisage 4.3.0-2',
                'etsdevtools 4.0.2-1',
                'etsproxy 0.1.2-1',
                'graphcanvas 4.0.2-1',
                'mayavi 4.3.0-3',
                'pyface 4.3.0-2',
                'scimath 4.1.2-2',
                'traits 4.3.0-2',
                'traitsui 4.3.0-2'],
            product='commercial',
            python=py3compat.u('2.7'),
            size=py3compat.long(10027),
            type='egg',
            version=py3compat.u('4.3.0'))

        path = op.join(DATA_DIR, "ets-4.3.0-3.egg")

        index_entry = EnpkgS3IndexEntry.from_egg(path)
        self.maxDiff = 2048
        self.assertEqual(r_data, index_entry.to_dict())

    def test_from_data(self):
        json_data = """\
{
    "available": false,
    "build": 1,
    "md5": "efaf1e95fe51ffc7b07219668d4d5a29",
    "mtime": 1.0,
    "egg_basename": "numpy",
    "packages": [
      "MKL 10.3-1"
    ],
    "python": "2.7",
    "size": 3251940,
    "type": "egg",
    "version": "1.7.1"
}
"""
        index_entry = EnpkgS3IndexEntry.from_data(json.loads(json_data))

        self.assertEqual(index_entry.name, py3compat.u("numpy"))

    def test_cased_egg_basename(self):
        path = op.join(DATA_DIR, "Cython-0.19.1-1.egg")

        index_entry = EnpkgS3IndexEntry.from_egg(path)
        self.assertEqual(index_entry.name, py3compat.u("cython"))
        self.assertEqual(index_entry.egg_basename, py3compat.u("Cython"))

    def test_enpkg_s3index_key(self):
        path = op.join(DATA_DIR, "Cython-0.19.1-1.egg")

        entry = EnpkgS3IndexEntry.from_egg(path)
        self.assertEqual(entry.s3index_key, "Cython-0.19.1-1.egg")

    def test_enpkg_s3index_data(self):
        r_data = {
            "available": True,
            "build": 1,
            "md5": "fa334276ff97c721370516530a36c475",
            "mtime": CYTHON_MTIME,
            "name": "cython",
            "packages": [],
            "product": "commercial",
            "python": "2.7",
            "size": CYTHON_SIZE,
            "type": "egg",
            "version": "0.19.1",
        }
        path = op.join(DATA_DIR, "Cython-0.19.1-1.egg")

        entry = EnpkgS3IndexEntry.from_egg(path, available=True)
        self.assertEqual(entry.s3index_data, r_data)
