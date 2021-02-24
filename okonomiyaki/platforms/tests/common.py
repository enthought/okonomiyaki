import collections
from unittest import mock
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
def _mock_distro_id(info):
    return Patcher(mock.patch("distro.id", lambda: info))


def _mock_distro_version(info):
    return Patcher(mock.patch("distro.version", lambda: info))

def _mock_distro_like(info):
    return Patcher(mock.patch("distro.like", lambda: info))


mock_centos_3_5 = MultiPatcher([
    mock_linux,
    _mock_distro_id("centos"), _mock_distro_version("3.5")])

mock_centos_5_8 = MultiPatcher([
    mock_linux,
    _mock_distro_id("centos"), _mock_distro_version("5.8")])

mock_centos_6_3 = MultiPatcher([
    mock_linux,
    _mock_distro_id("centos"), _mock_distro_version("6.3")])

mock_rhel_6_3 = MultiPatcher([
    mock_linux,
    _mock_distro_id("rhel"), _mock_distro_version("6.3")])

mock_centos_7_0 = MultiPatcher([
    mock_linux,
    _mock_distro_id("centos"), _mock_distro_version("7.0")])

mock_centos_7_6 = MultiPatcher([
    mock_linux,
    _mock_distro_id("centos"), _mock_distro_version("7.6.1810")])

mock_ubuntu = MultiPatcher([
    mock_linux,
    _mock_distro_id("ubuntu"), _mock_distro_version("13.04")])

mock_mint = MultiPatcher([
    mock_linux,
    _mock_distro_id("linuxmint"),
    _mock_distro_version("14.08"),
    _mock_distro_like("ubuntu")])

mock_debian = MultiPatcher([
    mock_linux,
    _mock_distro_id("debian"), _mock_distro_version("13.04")])

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
