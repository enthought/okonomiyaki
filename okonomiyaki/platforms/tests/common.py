import mock

from okonomiyaki.utils.testing import MultiPatcher, Patcher


# OS mocking
mock_darwin = Patcher(mock.patch("sys.platform", "darwin"))
mock_linux = Patcher(mock.patch("sys.platform", "linux2"))
mock_solaris = Patcher(mock.patch("sys.platform", "sunos5"))
mock_windows = Patcher(mock.patch("sys.platform", "win32"))


# OS Version mocking
def _mock_platform_dist(info):
    return Patcher(mock.patch("platform.dist", lambda: info))


def _mock_platform_linux_distribution(info):
    return Patcher(mock.patch("platform.linux_distribution", lambda: info))


mock_centos_3_5 = MultiPatcher([
    mock.patch("sys.platform", "linux2"),
    _mock_platform_dist(("redhat", "3.5", "Final")),
    _mock_platform_linux_distribution(("CentOS", "3.5", "Final"))
])

mock_centos_5_8 = MultiPatcher([
    mock.patch("sys.platform", "linux2"),
    _mock_platform_dist(("redhat", "5.8", "Final")),
    _mock_platform_linux_distribution(("CentOS", "5.8", "Final"))
])

mock_centos_6_3 = MultiPatcher([
    mock.patch("sys.platform", "linux2"),
    _mock_platform_dist(("redhat", "6.3", "Final")),
    _mock_platform_linux_distribution(("CentOS", "6.3", "Final"))
])

mock_centos_7_0 = MultiPatcher([
    mock.patch("sys.platform", "linux2"),
    _mock_platform_dist(("redhat", "7.0", "Final")),
    _mock_platform_linux_distribution(("CentOS", "7.0", "Final"))
])

mock_ubuntu_raring = MultiPatcher([
    _mock_platform_dist(("Ubuntu", "13.04", "raring")),
    _mock_platform_linux_distribution(("Ubuntu", "13.04", "raring")),
    mock.patch("sys.platform", "linux2"),
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
mock_machine = lambda machine: Patcher(mock.patch("platform.machine",
                                                  lambda: machine))

mock_machine_x86 = Patcher(mock_machine("x86"))
mock_architecture_32bit = Patcher(mock.patch("sys.maxsize", 2**32-1))

mock_machine_x86_64 = Patcher(mock_machine("x86_64"))
mock_architecture_64bit = Patcher(mock.patch("sys.maxsize", 2**64-1))

mock_x86 = MultiPatcher([mock_machine_x86, mock_architecture_32bit])
mock_x86_64 = MultiPatcher([mock_machine_x86_64, mock_architecture_64bit])
# A 32 bits python process on a 64 bits OS
mock_x86_on_x86_64 = MultiPatcher([mock_machine_x86_64,
                                   mock_architecture_32bit])

mock_machine_armv71 = Patcher(mock_machine("armv71"))
