import sys

from .._package_info import PackageInfo

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from ...errors import OkonomiyakiError
from .common import (
    BROKEN_MCCABE_EGG, PIP_EGG, PKG_INFO_ENSTALLER_1_0_DESCRIPTION,
    PIP_PKG_INFO, PKG_INFO_ENSTALLER_1_0, UNICODE_DESCRIPTION_EGG,
    UNICODE_DESCRIPTION_TEXT
)


class TestPackageInfo(unittest.TestCase):
    maxDiff = None

    def test_simple_from_string(self):
        # Given
        data = PKG_INFO_ENSTALLER_1_0
        r_description = PKG_INFO_ENSTALLER_1_0_DESCRIPTION

        # When
        pkg_info = PackageInfo.from_string(data)

        # Then
        self.assertEqual(pkg_info.name, "enstaller")
        self.assertEqual(pkg_info.version, "4.5.0")
        self.assertEqual(pkg_info.platforms, ())
        self.assertEqual(pkg_info.supported_platforms, ())
        self.assertEqual(
            pkg_info.summary,
            "Install and managing tool for egg-based packages"
        )
        self.assertMultiLineEqual(pkg_info.description, r_description)
        self.assertEqual(pkg_info.keywords, ())
        self.assertEqual(
            pkg_info.home_page, "https://github.com/enthought/enstaller"
        )
        self.assertEqual(pkg_info.download_url, "")
        self.assertEqual(pkg_info.author, "Enthought, Inc.")
        self.assertEqual(pkg_info.author_email, "info@enthought.com")
        self.assertEqual(pkg_info.license, "BSD")
        # classifiers is empty because we use metadata_info 1.0
        self.assertEqual(pkg_info.classifiers, ())
        self.assertEqual(pkg_info.requires, ())
        self.assertEqual(pkg_info.provides, ())
        self.assertEqual(pkg_info.obsoletes, ())

    def test_from_string_unsupported(self):
        # Given
        data = "Metadata-Version: 1.2"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            PackageInfo.from_string(data)

    def test_unsupported(self):
        # When/Then
        with self.assertRaises(OkonomiyakiError):
            PackageInfo("1.2", "numpy", "1.9.2")

    def test_simple_from_egg(self):
        # Given
        egg = PIP_EGG

        # When
        pkg_info = PackageInfo.from_egg(egg)

        # Then
        self.assertEqual(pkg_info.metadata_version, "1.1")
        self.assertEqual(pkg_info.name, "pip")
        self.assertEqual(pkg_info.version, "6.0.8")
        self.assertEqual(
            pkg_info.summary,
            "The PyPA recommended tool for installing Python packages."
        )

    def test_to_string(self):
        # Given
        egg = PIP_EGG
        r_pkg_info_s = PIP_PKG_INFO

        # When
        pkg_info = PackageInfo.from_egg(egg)

        # Then
        self.assertMultiLineEqual(pkg_info.to_string(), r_pkg_info_s)

    def test_from_broken_egg(self):
        # Given
        egg = BROKEN_MCCABE_EGG

        # When
        pkg_info = PackageInfo.from_egg(egg)

        # Then
        self.assertEqual(pkg_info.metadata_version, "1.1")
        self.assertEqual(pkg_info.name, "mccabe")
        self.assertEqual(pkg_info.version, "0.2.1")
        self.assertEqual(
            pkg_info.summary,
            "McCabe checker, plugin for flake8",
        )

    def test_from_egg_unicode(self):
        # Given
        egg = UNICODE_DESCRIPTION_EGG

        # When
        pkg_info = PackageInfo.from_egg(egg)

        # Then
        self.assertEqual(pkg_info.metadata_version, "1.1")
        self.assertEqual(pkg_info.name, "pymongo")
        self.assertEqual(pkg_info.version, "2.8")
        self.assertMultiLineEqual(
            pkg_info.description,
            UNICODE_DESCRIPTION_TEXT
        )
