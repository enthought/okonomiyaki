import json
import os
import unittest

import os.path as op

from okonomiyaki.models.grits import GritsEggEntry

DATA_DIR = op.join(op.dirname(__file__), "data")

__st = os.stat(op.join(DATA_DIR, "Cython-0.19.1-1.egg"))
CYTHON_MTIME = __st.st_mtime

class TestGritsEggEntry(unittest.TestCase):
    def test_cased_egg_basename(self):
        path = op.join(DATA_DIR, "Cython-0.19.1-1.egg")

        entry = GritsEggEntry.from_egg(path, "rh5-32", "free")
        self.assertEqual(entry.grits_key, "enthought/eggs/rh5-32/Cython-0.19.1-1.egg")
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
        r_metadata = {'build': 1L,
                'egg_basename': u'Cython',
                'md5': u'fa334276ff97c721370516530a36c475',
                'mtime': CYTHON_MTIME,
                'name': u'cython',
                'packages': [],
                'platform': 'rh5-32',
                'product': 'commercial',
                'python': u'2.7',
                'size': 4766L,
                'type': 'egg',
                'version': u'0.19.1'}

        path = op.join(DATA_DIR, "Cython-0.19.1-1.egg")

        entry = GritsEggEntry.from_egg(path, "rh5-32", "commercial")
        self.assertEqual(entry.grits_metadata, r_metadata)
