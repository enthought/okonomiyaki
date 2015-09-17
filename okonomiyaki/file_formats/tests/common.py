# coding=utf-8
import io
import os.path

from ... import repositories

DATA_DIR = os.path.join(os.path.dirname(repositories.__file__),
                        "tests", "data")

ENSTALLER_EGG = os.path.join(DATA_DIR, "enstaller-4.5.0-1.egg")
ETS_EGG = os.path.join(DATA_DIR, "ets-4.3.0-3.egg")
FAKE_PYSIDE_1_1_0_EGG = os.path.join(DATA_DIR, "PySide-1.1.0-3.egg")
MKL_EGG = os.path.join(DATA_DIR, "MKL-10.3-1.egg")
NUMEXPR_2_2_2_EGG = os.path.join(DATA_DIR, "numexpr-2.2.2-3.egg")
PIP_EGG = os.path.join(DATA_DIR, "pip-6.0.8-1.egg")
PYMULTINEST_EGG = os.path.join(DATA_DIR, "pymultinest-0.1-1.egg")
SUPERVISOR_EGG = os.path.join(DATA_DIR, "supervisor-3.0-1.egg")
XZ_5_2_0_EGG = os.path.join(DATA_DIR, "xz-5.2.0-1.egg")
PYSIDE_1_0_3_EGG = os.path.join(DATA_DIR, "PySide-1.0.3-1.egg")
_OSX64APP_EGG = os.path.join(DATA_DIR, "_osx64app-1.0-1.egg")

# Some eggs are for some reason built without EGG-INFO/PKG-INFO. A few
# eggs were built in a broken way, and some explicitly with this feature
# (see dcdd2492066b9a88e1cf39459c3fff99589f789d in buildsystem).
# In most of those cases, the PKG-INFO is instead written as
# EGG-INFO/PKG-INFO.bak (don't ask).
BROKEN_MCCABE_EGG = os.path.join(DATA_DIR, "broken_legacy_eggs",
                                 "mccabe-0.2.1-2.egg")

UNICODE_DESCRIPTION_EGG = os.path.join(DATA_DIR, "pymongo-2.8-1.egg")
with io.open(
    os.path.join(DATA_DIR, "pymongo_description.txt"),
    "r", encoding="utf8"
) as fp:
    UNICODE_DESCRIPTION_TEXT = fp.read()

# flake8: noqa
PKG_INFO_ENSTALLER_1_0 = u"""\
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

PKG_INFO_ENSTALLER_1_0_DESCRIPTION = u"""\
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
all EPD installers already include Enstaller.
"""

# flake8: noqa
PIP_PKG_INFO = u"""\
Metadata-Version: 1.1
Name: pip
Version: 6.0.8
Summary: The PyPA recommended tool for installing Python packages.
Home-page: https://pip.pypa.io/
Author: The pip developers
Author-email: python-virtualenv@groups.google.com
License: MIT
Description: pip
        ===
        
        The `PyPA recommended
        <https://python-packaging-user-guide.readthedocs.org/en/latest/current.html>`_
        tool for installing Python packages.
        
        * `Installation <https://pip.pypa.io/en/latest/installing.html>`_
        * `Documentation <https://pip.pypa.io/>`_
        * `Changelog <https://pip.pypa.io/en/latest/news.html>`_
        * `Github Page <https://github.com/pypa/pip>`_
        * `Issue Tracking <https://github.com/pypa/pip/issues>`_
        * `Mailing list <http://groups.google.com/group/python-virtualenv>`_
        * User IRC: #pypa on Freenode.
        * Dev IRC: #pypa-dev on Freenode.
        
        
        .. image:: https://pypip.in/v/pip/badge.png
                :target: https://pypi.python.org/pypi/pip
        
        .. image:: https://secure.travis-ci.org/pypa/pip.png?branch=develop
           :target: http://travis-ci.org/pypa/pip
        
Keywords: easy_install distutils setuptools egg virtualenv
Platform: UNKNOWN
Classifier: Development Status :: 5 - Production/Stable
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Topic :: Software Development :: Build Tools
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.2
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: 3.4
Classifier: Programming Language :: Python :: Implementation :: PyPy
"""

TRAITS_SETUPTOOLS_EGG = os.path.join(
    DATA_DIR, "traits-4.6.0.dev235-py2.7-macosx-10.10-intel.egg"
)

PIP_SETUPTOOLS_EGG = os.path.join(DATA_DIR, "pip-7.0.3-py3.4.egg")

FAKE_PYSIDE_1_1_0_EGG_PKG_INFO = u"""\
============
About PySide
============

PySide is the Nokia-sponsored Python Qt bindings project, providing access to
not only the complete Qt 4.7 framework but also Qt Mobility, as well as to
generator tools for rapidly generating bindings for any C++ libraries.

The PySide project is developed in the open, with all facilities you’d expect
from any modern OSS project such as all code in a git repository [1], an open
Bugzilla [2] for reporting bugs, and an open design process [3]. We welcome
any contribution without requiring a transfer of copyright.

=======
Changes
=======

1.1.0 (2012-01-02)
==================

Major changes
-------------

- New type converter scheme

Bug fixes
---------

- 1010 Shiboken Cygwin patch
- 1034 Error compiling PySide with Python 3.2.2 32bit on Windows
- 1040 pyside-uic overwriting attributes before they are being used
- 1053 pyside-lupdate used with .pro files can't handle Windows paths that contain spaces
- 1060 Subclassing of QUiLoader leads to "Internal C++ object already deleted" exception
- 1063 Bug writing to files using "QTextStream + QFile + QTextEdit" on Linux
- 1069 QtCore.QDataStream silently fails on writing Python string
- 1077 Application exit crash when call QSyntaxHighlighter.document()
- 1082 OSX binary links are broken
- 1083 winId returns a PyCObject making it impossible to compare two winIds
- 1084 Crash (segfault) when writing unicode string on socket
- 1091 PixmapFragment and drawPixmapFragments are not bound
- 1095 No examples for shiboken tutorial
- 1097 QtGui.QShortcut.setKey requires QKeySequence
- 1101 Report invalid function signatures in typesystem
- 902 Expose Shiboken functionality through a Python module
- 969 viewOptions of QAbstractItemView error

1.0.9 (2011-11-29)
==================

Bug fixes
---------

- 1058 Strange code in PySide/QtUiTools/glue/plugins.h
- 1057 valgrind detected “Conditional jump or move depends on uninitialised value”
- 1052 PySideConfig.cmake contains an infinite loop due to missing default for SHIBOKEN_PYTHON_SUFFIX
- 1048 QGridLayout.itemAtPosition() crashes when it should return None
- 1037 shiboken fails to build against python 3.2 (both normal and -dbg) on i386 (and others)
- 1036 Qt.KeyboardModifiers always evaluates to zero
- 1033 QDialog.DialogCode instances and return value from QDialog.exec_ hash to different values
- 1031 QState.parentState() or QState.machine() causes python crash at exit
- 1029 qmlRegisterType Fails to Increase the Ref Count
- 1028 QWidget winId missing
- 1016 Calling of Q_INVOKABLE method returning not QVariant is impossible…
- 1013 connect to QSqlTableModel.primeInsert() causes crash
- 1012 FTBFS with hardening flags enabled
- 1011 PySide Cygwin patch
- 1010 Shiboken Cygwin patch
- 1009 GeneratorRunner Cygwin patch
- 1008 ApiExtractor Cygwin patch
- 891 ApiExtractor doesn’t support doxygen as backend to doc generation.

1.0.8 (2011-10-21)
==================

Major changes
-------------

- Experimental Python3.2 support
- Qt4.8 beta support
- Bug Fixes

Bug fixes
---------

- 1022 RuntimeError: maximum recursion depth exceeded while getting the str of an object
- 1019 Overriding QWidget.show or QWidget.hide do not work
- 944 Segfault on QIcon(None).pixmap()

1.0.7 (2011-09-21)
==================

Bug fixes
---------

- 996 Missing dependencies for QtWebKit in buildscripts for Fedora
- 986 Documentation links
- 985 Provide versioned pyside-docs zip file to help packagers
- 981 QSettings docs should empathize the behavior changes of value() on different platforms
- 902 Expose Shiboken functionality through a Python module
- 997 QDeclarativePropertyMap doesn’t work.
- 994 QIODevice.readData must use qmemcpy instead of qstrncpy
- 989 Pickling QColor fails
- 987 Disconnecting a signal that has not been connected
- 973 shouldInterruptJavaScript slot override is never called
- 966 QX11Info.display() missing
- 959 can’t pass QVariant to the QtWebkit bridge
- 1006 Segfault in QLabel init
- 1002 Segmentation fault on PySide/Spyder exit
- 998 Segfault with Spyder after switching to another app
- 995 QDeclarativeView.itemAt returns faulty reference. (leading to SEGFAULT)
- 990 Segfault when trying to disconnect a signal that is not connected
- 975 Possible memory leak
- 991 The __repr__ of various types is broken
- 988 The type supplied with currentChanged signal in QTabWidget has changed in 1.0.6

1.0.6 (2011-08-22)
==================

Major changes
-------------

- New documentation layout;
- Fixed some regressions from the last release (1.0.5);
- Optimizations during anonymous connection;

Bug fixes
---------

- 972 anchorlayout.py of graphicsview example raised a unwriteable memory exception when exits
- 953 Segfault when QObject is garbage collected after QTimer.singeShot
- 951 ComponentComplete not called on QDeclarativeItem subclass
- 965 Segfault in QtUiTools.QUiLoader.load
- 958 Segmentation fault with resource files
- 944 Segfault on QIcon(None).pixmap()
- 941 Signals with QtCore.Qt types as arguments has invalid signatures
- 964 QAbstractItemView.moveCursor() method is missing
- 963 What’s This not displaying QTableWidget column header information as in Qt Designer
- 961 QColor.__repr__/__str__ should be more pythonic
- 960 QColor.__reduce__ is incorrect for HSL colors
- 950 implement Q_INVOKABLE
- 940 setAttributeArray/setUniformValueArray do not take arrays
- 931 isinstance() fails with Signal instances
- 928 100’s of QGraphicItems with signal connections causes slowdown
- 930 Documentation mixes signals and functions.
- 923 Make QScriptValue (or QScriptValueIterator) implement the Python iterator protocol
- 922 QScriptValue’s repr() should give some information about its data
- 900 QtCore.Property as decorator
- 895 jQuery version is outdated, distribution code de-duplication breaks documentation search
- 731 Can’t specify more than a single ’since’ argument
- 983 copy.deepcopy raises SystemError with QColor
- 947 NETWORK_ERR during interaction QtWebKit window with server
- 873 Deprecated methods could emit DeprecationWarning
- 831 PySide docs would have a “Inherited by” list for each class

1.0.5 (2011-07-22)
==================

Major changes
-------------

- Widgets present on “ui” files are exported in the root widget, check PySide ML thread for more information[1];
- pyside-uic generate menubars without parent on MacOS plataform;
- Signal connection optimizations;

Bug fixes
---------

- 892 Segfault when destructing QWidget and QApplication has event filter installed
- 407 Crash while multiple inheriting with QObject and native python class
- 939 Shiboken::importModule must verify if PyImport_ImportModule succeeds
- 937 missing pid method in QProcess
- 927 Segfault on QThread code.
- 925 Segfault when passing a QScriptValue as QObject or when using .toVariant() on a QScriptValue
- 905 QtGui.QHBoxLayout.setMargin function call is created by pyside-uic, but this is not available in the pyside bindings
- 904 Repeatedly opening a QDialog with Qt.WA_DeleteOnClose set crashes PySide
- 899 Segfault with ‘QVariantList’ Property.
- 893 Shiboken leak reference in the parent control
- 878 Shiboken may generate incompatible modules if a new class is added.
- 938 QTemporaryFile JPEG problem
- 934 A __getitem__ of QByteArray behaves strange
- 929 pkg-config files do not know about Python version tags
- 926 qmlRegisterType does not work with QObject
- 924 Allow QScriptValue to be accessed via []
- 921 Signals not automatically disconnected on object destruction
- 920 Cannot use same slot for two signals
- 919 Default arguments on QStyle methods not working
- 915 QDeclarativeView.scene().addItem(x) make the x object invalid
- 913 Widgets inside QTabWidget are not exported as members of the containing widget
- 910 installEventFilter() increments reference count on target object
- 907 pyside-uic adds MainWindow.setMenuBar(self.menubar) to the generated code under OS X
- 903 eventFilter in ItemDelegate
- 897 QObject.property() and QObject.setProperty() methods fails for user-defined properties
- 896 QObject.staticMetaObject() is missing
- 916 Missing info about when is possible to use keyword arguments in docs [was: QListWidgetItem's constructor ignores text parameter]
- 890 Add signal connection example for valueChanged(int) on QSpinBox to the docs
- 821 Mapping interface for QPixmapCache
- 909 Deletion of QMainWindow/QApplication leads to segmentation fault

==========
References
==========

- [1] http://qt.gitorious.org/pyside
- [2] http://bugs.openbossa.org/
- [3] http://www.pyside.org/docs/pseps/psep-0001.html
- [4] http://developer.qt.nokia.com/wiki/PySideDownloads
"""
