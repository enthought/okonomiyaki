# coding=utf-8
import os.path


PYSIDE_1_0_7_PKG_INFO = u"""\
Metadata-Version: 1.0
Name: PySide
Version: 1.0.7qt474
Summary: Python bindings for the Qt cross-platform application and UI framework
Home-page: http://www.pyside.org
Author: PySide Team
Author-email: contact@pyside.org
License: LGPL
Description: PySide is the Nokia-sponsored Python Qt bindings project, providing access to
        not only the complete Qt 4.7 framework but also Qt Mobility, as well as to
        generator tools for rapidly generating bindings for any C++ libraries.
        
        The PySide project is developed in the open, with all facilities you’d expect
        from any modern OSS project such as all code in a git repository [1], an open
        Bugzilla [2] for reporting bugs, and an open design process [3]. We welcome
        any contribution without requiring a transfer of copyright.
        
        =======
        Changes
        =======
        
        1.0.7 (released 21.09.2011)
        ===========================
        
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
        
        1.0.6 (released 22.08.2011)
        ===========================
        
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
        
        1.0.5 (released 22.07.2011)
        ===========================
        
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
        
Keywords: Qt
Platform: UNKNOWN
Classifier: Development Status :: 4 - Beta
Classifier: Environment :: Console
Classifier: Environment :: MacOS X
Classifier: Environment :: X11 Applications :: Qt
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Classifier: Operating System :: MacOS :: MacOS X
Classifier: Operating System :: POSIX
Classifier: Operating System :: POSIX :: Linux
Classifier: Programming Language :: C++
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2
Classifier: Topic :: Database
Classifier: Topic :: Software Development
Classifier: Topic :: Software Development :: Code Generators
Classifier: Topic :: Software Development :: Libraries :: Application Frameworks
Classifier: Topic :: Software Development :: User Interfaces
Classifier: Topic :: Software Development :: Widget Sets
"""

PYSIDE_1_0_8_PKG_INFO = u"""\
Metadata-Version: 1.0
Name: PySide
Version: 1.0.8qt474
Summary: Python bindings for the Qt cross-platform application and UI framework
Home-page: http://www.pyside.org
Author: PySide Team
Author-email: contact@pyside.org
License: LGPL
Description: ============
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
        
Keywords: Qt
Platform: UNKNOWN
Classifier: Development Status :: 4 - Beta
Classifier: Environment :: Console
Classifier: Environment :: MacOS X
Classifier: Environment :: X11 Applications :: Qt
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Classifier: Operating System :: MacOS :: MacOS X
Classifier: Operating System :: POSIX
Classifier: Operating System :: POSIX :: Linux
Classifier: Programming Language :: C++
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2
Classifier: Topic :: Database
Classifier: Topic :: Software Development
Classifier: Topic :: Software Development :: Code Generators
Classifier: Topic :: Software Development :: Libraries :: Application Frameworks
Classifier: Topic :: Software Development :: User Interfaces
Classifier: Topic :: Software Development :: Widget Sets
"""

PYSIDE_1_0_9_PKG_INFO = u"""\
Metadata-Version: 1.0
Name: PySide
Version: 1.0.9qt474
Summary: Python bindings for the Qt cross-platform application and UI framework
Home-page: http://www.pyside.org
Author: PySide Team
Author-email: contact@pyside.org
License: LGPL
Description: ============
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
        
Keywords: Qt
Platform: UNKNOWN
Classifier: Development Status :: 4 - Beta
Classifier: Environment :: Console
Classifier: Environment :: MacOS X
Classifier: Environment :: X11 Applications :: Qt
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Classifier: Operating System :: MacOS :: MacOS X
Classifier: Operating System :: POSIX
Classifier: Operating System :: POSIX :: Linux
Classifier: Programming Language :: C++
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2
Classifier: Topic :: Database
Classifier: Topic :: Software Development
Classifier: Topic :: Software Development :: Code Generators
Classifier: Topic :: Software Development :: Libraries :: Application Frameworks
Classifier: Topic :: Software Development :: User Interfaces
Classifier: Topic :: Software Development :: Widget Sets
"""

PYSIDE_1_1_0_PKG_INFO = u"""\
Metadata-Version: 1.0
Name: PySide
Version: 1.1.0qt474
Summary: Python bindings for the Qt cross-platform application and UI framework
Home-page: http://www.pyside.org
Author: PySide Team
Author-email: contact@pyside.org
License: LGPL
Description: ============
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
        
Keywords: Qt
Platform: UNKNOWN
Classifier: Development Status :: 4 - Beta
Classifier: Environment :: Console
Classifier: Environment :: MacOS X
Classifier: Environment :: X11 Applications :: Qt
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Classifier: Operating System :: MacOS :: MacOS X
Classifier: Operating System :: POSIX
Classifier: Operating System :: POSIX :: Linux
Classifier: Programming Language :: C++
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2
Classifier: Topic :: Database
Classifier: Topic :: Software Development
Classifier: Topic :: Software Development :: Code Generators
Classifier: Topic :: Software Development :: Libraries :: Application Frameworks
Classifier: Topic :: Software Development :: User Interfaces
Classifier: Topic :: Software Development :: Widget Sets
"""


# egg's sha256 to correcty decoded PKG_INFO content
_EGG_PKG_INFO_BLACK_LIST = {
    "PySide-1.0.7-1.egg": {
        "ca0903cc398aa69da1939be22bac52941ac2d8dd0a197eb2c449fdddd6339f80":
            PYSIDE_1_0_7_PKG_INFO,
        "946211c1f20f01bb5a29ec8783acd74a5ed234b3ced88a5256861077b2f1c34d":
            PYSIDE_1_0_7_PKG_INFO,
    },
    "PySide-1.0.8-1.egg": {
        "79174bb334fddb06a970e8e61f78c94d90259ca10dd85f88516c02bf4f135f45":
            PYSIDE_1_0_8_PKG_INFO,
    },
    "PySide-1.0.8-2.egg": {
        "79174bb334fddb06a970e8e61f78c94d90259ca10dd85f88516c02bf4f135f45":
            PYSIDE_1_0_8_PKG_INFO,
    },
    "PySide-1.0.9-1.egg": {
        "8d880887fb8155329888decdd8fc1fdbce1a214da9a98206a64f0ee57b554279":
            PYSIDE_1_0_9_PKG_INFO,
        "8d1ff3f8713c84cc8aa36cbac49051b094ecb2863b8dfa1b5ccd737ae82c14a8":
            PYSIDE_1_0_9_PKG_INFO,
    },
    "PySide-1.1.0-2.egg": {
        "16644aaaa1d2447677634d6dfe8fc5f9890be731641c4f46448646d1c409c656":
            PYSIDE_1_1_0_PKG_INFO,
        "c0a73ef8843e0934287e57d0812b2b9024587bb034f6146ce0999207366edc4d":
            PYSIDE_1_1_0_PKG_INFO,
    },
    "PySide-1.1.0-3.egg": {
        "5eff70cfb464c2d531e6f93f7601e8ef8255b3a1ab4dd533826cfdcd5b962b60":
            PYSIDE_1_1_0_PKG_INFO,
        "afb7402aa38ccef4ed5d0233807bb6611b59e24106fc27f6d271b11cf9562454":
            PYSIDE_1_1_0_PKG_INFO,
    }
}

EGG_PKG_INFO_BLACK_LIST = dict(
    (checksum, pkg_info_data)
    for egg in _EGG_PKG_INFO_BLACK_LIST.values()
    for checksum, pkg_info_data in egg.items()
)


def may_be_in_pkg_info_blacklist(path):
    """ Returns True if the given egg path may be in the PKG INFO blacklist.
    """
    return os.path.basename(path) in _EGG_PKG_INFO_BLACK_LIST
