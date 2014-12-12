import mock

from okonomiyaki.utils.testing import MultiPatcher, Patcher


mock_darwin = Patcher(mock.patch("sys.platform", "darwin"))
mock_linux = Patcher(mock.patch("sys.platform", "linux2"))
mock_solaris = Patcher(mock.patch("sys.platform", "sunos5"))
mock_windows = Patcher(mock.patch("sys.platform", "win32"))


def mock_platform_dist(info):
    return Patcher(mock.patch("platform.dist", lambda: info))


mock_centos_3_5 = Patcher(mock_platform_dist(("redhat", "3.5", "Final")))
mock_centos_5_8 = Patcher(mock_platform_dist(("redhat", "5.8", "Final")))
mock_centos_6_3 = Patcher(mock_platform_dist(("centos", "6.4", "Final")))

mock_ubuntu_raring = Patcher(mock_platform_dist(("Ubuntu", "13.04", "raring")))

mock_machine = lambda machine: Patcher(mock.patch("platform.machine",
                                                  lambda: machine))
mock_architecture = lambda arch: Patcher(mock.patch("platform.architecture",
                                                    lambda: arch))

mock_machine_x86 = Patcher(mock_machine("x86"))
mock_architecture_32bit = Patcher(mock_architecture(("32bit",)))

mock_machine_x86_64 = Patcher(mock_machine("x86_64"))
mock_architecture_64bit = Patcher(mock_architecture(("64bit",)))

mock_x86 = MultiPatcher([mock_machine_x86, mock_architecture_32bit])
mock_x86_64 = MultiPatcher([mock_machine_x86_64, mock_architecture_64bit])

mock_machine_armv71 = Patcher(mock_machine("armv71"))
