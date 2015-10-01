from __future__ import absolute_import

import platform
import sys

import six

from ..bundled.traitlets import HasTraits, Enum, Instance, Unicode
from ..errors import OkonomiyakiError

from ._arch import Arch
from .python_implementation import PythonImplementation


DARWIN = "darwin"
LINUX = "linux"
SOLARIS = "solaris"
WINDOWS = "windows"

CENTOS = "centos"
DEBIAN = "debian"
RHEL = "rhel"
UBUNTU = "ubuntu"
MAC_OS_X = "mac_os_x"

NAME_TO_PRETTY_NAMES = {
    WINDOWS: "Windows",
    MAC_OS_X: "Mac OS X",
    CENTOS: "CentOS",
    RHEL: "RedHat",
    UBUNTU: "Ubuntu",
    DEBIAN: "Debian",
}

_DIST_NAME_TO_NAME = {
    "centos": CENTOS,
    "redhat": RHEL,
    "ubuntu": UBUNTU,
    "debian": DEBIAN,
}


def default_abi(platform, python_implementation):
    """ Returns the default abi for the given platform and python
    implementation.

    Parameters
    ----------
    platform : Platform
        The platform to get the default abi for
    python_implementation : str or PythonImplementation
        If a string (e.g. 'cp27'), will be converted into a
        PythonImplementation.
    """
    if isinstance(python_implementation, six.text_type):
        python_implementation = PythonImplementation.from_string(
            python_implementation
        )

    msg = (
        "Unsupported platform/python implementation combo: {0!r}/{1!r}".
        format(platform, python_implementation)
    )

    if platform.os == DARWIN:
        return u"darwin"
    elif platform.os == LINUX:
        return u"gnu"
    elif platform.os == WINDOWS:
        abi = None
        if python_implementation.major == 2:
            abi = u"msvc2008"
        elif python_implementation.major == 3:
            if python_implementation.minor <= 4:
                abi = u"msvc2010"
            elif python_implementation.minor == 5:
                abi = u"msvc2015"
        if abi is None:
            raise OkonomiyakiError(msg)

        return abi
    else:
        raise OkonomiyakiError(msg)


class Platform(HasTraits):
    """
    An sane generic platform representation.
    """
    os = Enum([WINDOWS, LINUX, DARWIN, SOLARIS])
    """
    The most generic OS description
    """

    name = Enum([WINDOWS, CENTOS, RHEL, DEBIAN, UBUNTU, MAC_OS_X, SOLARIS])
    """
    The most specific platform description
    """

    family = Enum([WINDOWS, RHEL, DEBIAN, MAC_OS_X, SOLARIS])
    """
    The 'kind' of platforms. For example, both debian and ubuntu distributions
    share the same kind, 'debian'.
    """

    release = Unicode()
    """
    The release string. May be empty
    """

    arch = Instance(Arch)
    """
    Actual architecture. The architecture is guessed from the running python.
    """

    machine = Instance(Arch)
    """
    The machine (e.g. 'x86'). This is the CPU architecture (e.g. a 32 bits
    python running on 64 bits Intel OS will be 'amd64', whereas arch will be
    'x86')
    """

    @classmethod
    def from_running_python(cls):
        """ Guess the platform, using the running python to guess the
        architecture.
        """
        return _guess_platform()

    @classmethod
    def from_running_system(cls, arch_string=None):
        """ Guess the platform, with an optional architecture string.

        Parameters
        ----------
        arch_string: str, None
            If given, should be a valid architecture name (e.g. 'x86')
        """
        return _guess_platform(arch_string)

    def __init__(self, os, name, family, arch, machine=None, release=""):
        super(Platform, self).__init__(os=os, name=name, family=family,
                                       arch=arch, machine=machine,
                                       release=release)
        if machine is None:
            self.machine = self.arch

    def __repr__(self):
        return (
            "Platform(os={0.os!r}, name={0.name!r}, family={0.family!r}, "
            "arch='{0.arch}', machine='{0.machine}')".format(self)
        )

    def __str__(self):
        return "{0} {1.release} on {1.machine}".format(
            NAME_TO_PRETTY_NAMES[self.name],
            self
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        else:
            return (self.name == other.name and self.release == other.release
                    and self.arch == other.arch
                    and self.machine == other.machine)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.name, self.release, self.arch, self.machine))


def _guess_os():
    if sys.platform == "win32":
        return WINDOWS
    elif sys.platform == "darwin":
        return DARWIN
    elif sys.platform.startswith("linux"):
        return LINUX
    else:
        msg = "Could not guess platform from sys.platform: {0!r}"
        raise OkonomiyakiError(msg.format(sys.platform))


def _guess_platform_details(os):
    if os == WINDOWS:
        return WINDOWS, WINDOWS, platform.win32_ver()[0]
    elif os == DARWIN:
        return MAC_OS_X, MAC_OS_X, platform.mac_ver()[0]
    elif os == LINUX:
        name = platform.linux_distribution()[0].lower()
        _, release, _ = platform.dist()
        if name in (DEBIAN, UBUNTU):
            family = DEBIAN
        elif name in (CENTOS, RHEL):
            family = RHEL
        else:
            raise OkonomiyakiError("Unsupported platform: {0!r}".format(name))
        return name, family, release


def _guess_platform(arch_string=None):
    if arch_string is None:
        arch = Arch.from_running_python()
    else:
        arch = Arch.from_name(arch_string)

    machine = Arch.from_running_system()
    os = _guess_os()
    name, family, release = _guess_platform_details(os)

    return Platform(os=os, name=name, family=family, release=release,
                    arch=arch, machine=machine)
