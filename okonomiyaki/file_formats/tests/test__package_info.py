import os.path
import sys

from .._package_info import PackageInfo

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from okonomiyaki import repositories


DATA_DIR = os.path.join(os.path.dirname(repositories.__file__), "tests",
                        "data")

ENSTALLER_EGG = os.path.join(DATA_DIR, "enstaller-4.5.0-1.egg")
PIP_EGG = os.path.join(DATA_DIR, "pip-6.0.8-1.egg")

# flake8: noqa
PKG_INFO_ENSTALLER_1_0 = """\
Metadata-Version: 1.0
Name: enstaller
Version: 4.5.0
Summary: Install and managing tool for egg-based packages
Home-page: https://github.com/enthought/enstaller
Author: Enthought, Inc.
Author-email: info@enthought.com
License: BSD
Description: The Enstaller (version 4) project is a managing and install tool
        for egg-based Python distributions.
        
        Enstaller consists of the sub-packages enstaller (package managing
        tool) and egginst (package (un)install tool).  We find the clean
        separation into these two tasks, each of which having a well-defined
        scope, extremely useful.
        
        
        enstaller:
        ----------
        
        enstaller is a managing tool for egginst-based installs, and the CLI is
        called enpkg which calls out to egginst to do the actual install.
        enpkg can access distributions from local and HTTP repositories, which
        are pre-indexed.  The point of the index file (index-depend.bz2) is that
        enpkg can download this file at the beginning of an install session
        and resolve dependencies prior to downloading the actual files.
        
        
        egginst:
        --------
        
        egginst is the underlying tool for installing and uninstalling eggs.
        The tool is brain dead in the sense that it does not care if the eggs
        it installs are for the correct platform, it's dependencies got installed,
        another package needs to be uninstalled prior to the install, and so on.
        Those tasks are responsibilities of a package manager, and are outside
        the scope of egginst.
        
        egginst installs modules and packages directly into site-packages, i.e.
        no .egg directories are created, hence there is no extra .pth-file which
        results in a sorter python path and faster import times (which seems to
        have the biggest advantage for namespace packages).  egginst knows about
        the eggs the people from Enthought use.  It can install shared libraries,
        change binary headers, etc., things which would require special post install
        scripts if easy_install installs them.
        
        
        The egg format:
        ---------------
        
        The Enstaller egg format deals with two aspects: the actual install (egginst),
        and the distribution management (enpkg).  As far as egginst is concerned,
        the format is an extension of the setuptools egg format, i.e. all archive
        files, except the ones starting with 'EGG-INFO/' are installed into the
        site-packages directory.  In fact, since egginst a brain dead low-level tool,
        it will even install an egg without an 'EGG-INFO' directory.  But more
        importantly, egginst installs ordinary setuptools just fine.  Within the
        'EGG-INFO/' namespace are special archives which egginst is looking for to
        install files, as well as symbolic links, into locations other than
        site-packages, and post install (and pre uninstall) scripts it can run.
        
        As far as enpkg is concerned, eggs should contain a meta-data file with the
        archive name 'EGG-INFO/spec/depend'.  The the index file (index-depend.bz2)
        is essentially a compressed concatenation of the 'EGG-INFO/spec/depend' files
        for all eggs in a directory/repository.
        
        
        Egg file name format:
        ---------------------
        
        Eggs follow the following naming convention::
        
           <name>-<version>-<build>.egg
        
        ``<name>``
           The package name, which may contain the following characters:
           Letters (both lower or uppercase), digits, underscore '_' and a dot '.'
        
        ``<version>``
           The version number, which is restricted to containing the
           same characters as the package name, and which should
           follow `PEP 386 <http://www.python.org/dev/peps/pep-0386/>`_.
        
        ``<build>``
           The build number, which may only contains digits (with no leading zeros).
           This number is used to distinguish between different eggs which were build
           from the same project source.  Having different build numbers becomes
           necessary when, for example: eggs are build for different Python versions,
           a build bug is fixed, a patch is applied to the source, etc. .
        
        The regular expression for a valid egg file name is::
        
           r'([\w.]+)-([\w.]+)-(\d+)\.egg$'
        
        
        The metadata format:
        --------------------
        
        Build numbers are a way to differentiate eggs which have the have the
        same name and version, but different dependencies.  The platform and
        architecture dependencies of a distributions (or egg) is most easily
        differentiated by putting them into different directories.  This leaves
        us with the Python dependency and other egg dependencies to put into the
        build number.  A dependencies specification data file is contained inside
        the egg itself, that is in the archive ``EGG-INFO/spec/depend``, and the
        md5sum and filesize is prepended to the data when the index-depend.bz2 is
        created.
        
        
        Installation:
        -------------
        
        The preferred and easiest way to install Enstaller from the executable egg,
        e.i. the Enstaller egg contains a bash header, and on Unix system, you can
        also download the egg and type::
        
           $ bash enstaller-4.5.0-1.egg
           Bootstrapping: ...
           283 KB [.................................................................]
        
        Once Enstaller is installed, it is possible to update itself.  Note that,
        as Enstaller is the install tool for the Enthought Python Distribution (EPD),
        all EPD installers already include Enstaller.
        
Platform: UNKNOWN
Classifier: License :: OSI Approved :: BSD License
Classifier: Development Status :: 5 - Production/Stable
Classifier: Intended Audience :: Developers
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python :: 2.5
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Topic :: System :: Software Distribution
Classifier: Topic :: System :: Systems Administration
"""

PKG_INFO_ENSTALLER_1_0_DESCRIPTION = """\
The Enstaller (version 4) project is a managing and install tool
for egg-based Python distributions.

Enstaller consists of the sub-packages enstaller (package managing
tool) and egginst (package (un)install tool).  We find the clean
separation into these two tasks, each of which having a well-defined
scope, extremely useful.


enstaller:
----------

enstaller is a managing tool for egginst-based installs, and the CLI is
called enpkg which calls out to egginst to do the actual install.
enpkg can access distributions from local and HTTP repositories, which
are pre-indexed.  The point of the index file (index-depend.bz2) is that
enpkg can download this file at the beginning of an install session
and resolve dependencies prior to downloading the actual files.


egginst:
--------

egginst is the underlying tool for installing and uninstalling eggs.
The tool is brain dead in the sense that it does not care if the eggs
it installs are for the correct platform, it's dependencies got installed,
another package needs to be uninstalled prior to the install, and so on.
Those tasks are responsibilities of a package manager, and are outside
the scope of egginst.

egginst installs modules and packages directly into site-packages, i.e.
no .egg directories are created, hence there is no extra .pth-file which
results in a sorter python path and faster import times (which seems to
have the biggest advantage for namespace packages).  egginst knows about
the eggs the people from Enthought use.  It can install shared libraries,
change binary headers, etc., things which would require special post install
scripts if easy_install installs them.


The egg format:
---------------

The Enstaller egg format deals with two aspects: the actual install (egginst),
and the distribution management (enpkg).  As far as egginst is concerned,
the format is an extension of the setuptools egg format, i.e. all archive
files, except the ones starting with 'EGG-INFO/' are installed into the
site-packages directory.  In fact, since egginst a brain dead low-level tool,
it will even install an egg without an 'EGG-INFO' directory.  But more
importantly, egginst installs ordinary setuptools just fine.  Within the
'EGG-INFO/' namespace are special archives which egginst is looking for to
install files, as well as symbolic links, into locations other than
site-packages, and post install (and pre uninstall) scripts it can run.

As far as enpkg is concerned, eggs should contain a meta-data file with the
archive name 'EGG-INFO/spec/depend'.  The the index file (index-depend.bz2)
is essentially a compressed concatenation of the 'EGG-INFO/spec/depend' files
for all eggs in a directory/repository.


Egg file name format:
---------------------

Eggs follow the following naming convention::

   <name>-<version>-<build>.egg

``<name>``
   The package name, which may contain the following characters:
   Letters (both lower or uppercase), digits, underscore '_' and a dot '.'

``<version>``
   The version number, which is restricted to containing the
   same characters as the package name, and which should
   follow `PEP 386 <http://www.python.org/dev/peps/pep-0386/>`_.

``<build>``
   The build number, which may only contains digits (with no leading zeros).
   This number is used to distinguish between different eggs which were build
   from the same project source.  Having different build numbers becomes
   necessary when, for example: eggs are build for different Python versions,
   a build bug is fixed, a patch is applied to the source, etc. .

The regular expression for a valid egg file name is::

   r'([\w.]+)-([\w.]+)-(\d+)\.egg$'


The metadata format:
--------------------

Build numbers are a way to differentiate eggs which have the have the
same name and version, but different dependencies.  The platform and
architecture dependencies of a distributions (or egg) is most easily
differentiated by putting them into different directories.  This leaves
us with the Python dependency and other egg dependencies to put into the
build number.  A dependencies specification data file is contained inside
the egg itself, that is in the archive ``EGG-INFO/spec/depend``, and the
md5sum and filesize is prepended to the data when the index-depend.bz2 is
created.


Installation:
-------------

The preferred and easiest way to install Enstaller from the executable egg,
e.i. the Enstaller egg contains a bash header, and on Unix system, you can
also download the egg and type::

   $ bash enstaller-4.5.0-1.egg
   Bootstrapping: ...
   283 KB [.................................................................]

Once Enstaller is installed, it is possible to update itself.  Note that,
as Enstaller is the install tool for the Enthought Python Distribution (EPD),
all EPD installers already include Enstaller."""


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
        self.assertEqual(pkg_info.keywords, "")
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