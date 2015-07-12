import os
import unittest

import os.path as op

from ...utils import py3compat
from ..grits import GritsEggEntry

DATA_DIR = op.join(op.dirname(__file__), "data")

__st = os.stat(op.join(DATA_DIR, "Cython-0.19.1-1.egg"))
CYTHON_MTIME = __st.st_mtime


class TestGritsEggEntry(unittest.TestCase):
    def test_cased_egg_basename(self):
        path = op.join(DATA_DIR, "Cython-0.19.1-1.egg")

        entry = GritsEggEntry.from_egg(path, "rh5-32", "free")
        self.assertEqual(entry.grits_key,
                         "enthought/eggs/rh5-32/Cython-0.19.1-1.egg")
        self.assertEqual(entry.name, "cython")
        self.assertEqual(entry.egg_name, op.basename(path))

    def test_free_tags(self):
        value = ["enthought-free"]
        r_tags = {"accessible": value,
                  "modifiable": value,
                  "owned": value,
                  "visible": value,
                  "writable": value}

        path = op.join(DATA_DIR, "Cython-0.19.1-1.egg")

        entry = GritsEggEntry.from_egg(path, "rh5-32", "free")
        self.assertEqual(entry.grits_tags, r_tags)

    def test_commercial_tags(self):
        value = ["enthought-commercial", "enthought-academic"]
        r_tags = {"accessible": value,
                  "modifiable": value,
                  "owned": value,
                  "visible": ["enthought-free"],
                  "writable": value}

        path = op.join(DATA_DIR, "Cython-0.19.1-1.egg")

        entry = GritsEggEntry.from_egg(path, "rh5-32", "commercial")
        self.assertEqual(entry.grits_tags, r_tags)

    def test_metadata(self):
        r_metadata = {'build': py3compat.long(1),
                      'egg_basename': py3compat.u('Cython'),
                      'md5': py3compat.u('fa334276ff97c721370516530a36c475'),
                      'mtime': CYTHON_MTIME,
                      'name': py3compat.u('cython'),
                      'packages': [],
                      'platform': 'rh5-32',
                      'product': 'commercial',
                      'python': py3compat.u('2.7'),
                      'qa_level': py3compat.u('stable'),
                      'size': py3compat.long(4766),
                      'type': 'egg',
                      'version': py3compat.u('0.19.1'),
                      'qa_level': 'stable'}

        path = op.join(DATA_DIR, "Cython-0.19.1-1.egg")

        entry = GritsEggEntry.from_egg(path, "rh5-32", "commercial")
        self.assertEqual(entry.grits_metadata, r_metadata)

    def test_qa_level(self):

        path = op.join(DATA_DIR, "Cython-0.19.1-1.egg")

        entry = GritsEggEntry.from_egg(
            path, "rh5-32", "commercial", qa_level='staging'
        )
        self.assertEqual(entry.grits_metadata['qa_level'], 'staging')
