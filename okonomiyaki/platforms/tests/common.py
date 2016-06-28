import collections
import mock
import sys

from ...utils.testing import MultiPatcher, Patcher


# OS mocking
# XXX: We need to patch platform.uname as well, as that function is cached, and
# the result depend on sys.platform value.
uname_result = collections.namedtuple("uname_result",
                                      "system node release version machine "
                                      "processor")


def _mock_uname(*args):
    if sys.version_info[0] == 2:
        return args
    else:
        return uname_result(*args)

mock_darwin = MultiPatcher([
    mock.patch("sys.platform", "darwin"),
    mock.patch("platform.uname",
               lambda: _mock_uname("Darwin", "localhost", "11.4.2",
                                   "Darwin Kernel Version 11.4.2 bla bla",
                                   "x86_64", "i386")),
])

mock_linux = MultiPatcher([
    mock.patch("sys.platform", "linux2"),
    mock.patch("platform.uname",
               lambda: _mock_uname("Linux", "localhost", "2.6.19-308.el5",
                                   "#1 SMP Tue Feb 21 20:06:06 EST 2012",
                                   "x86_64", "x86_64"))
])
mock_solaris = MultiPatcher([
    mock.patch("sys.platform", "sunos5"),
    mock.patch("platform.uname",
               lambda: _mock_uname("Solaris", "localhost", "fake",
                                   "fake", "x86_64", "x86_64")),
])
mock_windows = MultiPatcher([
    mock.patch("sys.platform", "win32"),
    mock.patch("platform.uname",
               lambda: _mock_uname('Windows', 'localhost', '7', '6.1.7601',
                                   'x86',
                                   ('x86 Family 6 Model 4 5 Stepping 7, '
                                    'GenuineIntel')))
])


# OS Version mocking
def _mock_platform_dist(info):
    return Patcher(mock.patch("platform.dist", lambda: info))


def _mock_platform_linux_distribution(info):
    return Patcher(mock.patch("platform.linux_distribution", lambda: info))


mock_centos_3_5 = MultiPatcher([
    mock_linux,
    _mock_platform_dist(("redhat", "3.5", "Final")),
    _mock_platform_linux_distribution(("CentOS", "3.5", "Final"))
])

mock_centos_5_8 = MultiPatcher([
    mock_linux,
    _mock_platform_dist(("redhat", "5.8", "Final")),
    _mock_platform_linux_distribution(("CentOS", "5.8", "Final"))
])

mock_centos_6_3 = MultiPatcher([
    mock_linux,
    _mock_platform_dist(("redhat", "6.3", "Final")),
    _mock_platform_linux_distribution(("CentOS", "6.3", "Final"))
])

mock_centos_7_0 = MultiPatcher([
    mock_linux,
    _mock_platform_dist(("redhat", "7.0", "Final")),
    _mock_platform_linux_distribution(("CentOS", "7.0", "Final"))
])

mock_ubuntu_raring = MultiPatcher([
    _mock_platform_dist(("Ubuntu", "13.04", "raring")),
    _mock_platform_linux_distribution(("Ubuntu", "13.04", "raring")),
    mock_linux,
])

mock_windows_7 = MultiPatcher([
    mock.patch("sys.platform", "win32"),
    mock.patch("platform.win32_ver",
               lambda: ("7", "6.1.7601", "SP1", "Multiprocessor Free"))
])

mock_osx_10_7 = MultiPatcher([
    mock.patch("sys.platform", "darwin"),
    mock.patch("platform.mac_ver", lambda: ("10.7.5", ("", "", ""), "x86_64")),
])


# Architecture mocking
def mock_machine(machine):
    return Patcher(mock.patch("platform.machine", lambda: machine))


mock_machine_x86 = Patcher(mock_machine("x86"))
mock_architecture_32bit = Patcher(mock.patch("sys.maxsize", 2**32 - 1))

mock_machine_x86_64 = Patcher(mock_machine("x86_64"))
mock_architecture_64bit = Patcher(mock.patch("sys.maxsize", 2**64 - 1))

mock_x86 = MultiPatcher([mock_machine_x86, mock_architecture_32bit])
mock_x86_64 = MultiPatcher([mock_machine_x86_64, mock_architecture_64bit])
# A 32 bits python process on a 64 bits OS
mock_x86_on_x86_64 = MultiPatcher([mock_machine_x86_64,
                                   mock_architecture_32bit])

mock_machine_armv71 = Patcher(mock_machine("armv71"))
