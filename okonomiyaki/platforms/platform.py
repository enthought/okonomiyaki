from __future__ import absolute_import

import platform
import sys

from okonomiyaki.bundled.traitlets import HasTraits, Enum, Instance, Unicode
from okonomiyaki.platforms.epd_platform import EPDPlatform
from okonomiyaki.errors import OkonomiyakiError


X86 = "x86"
X86_64 = "x86_64"

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

_ARCH_NAME_TO_BITS = {
    X86: 32,
    X86_64: 64,
}

_DIST_NAME_TO_NAME = {
    "centos": CENTOS,
    "redhat": RHEL,
    "ubuntu": UBUNTU,
    "debian": DEBIAN,
}


class Arch(HasTraits):
    name = Enum([X86, X86_64])
    """
    Actual architecture name (e.g. 'x86'). The architecture is guessed from the
    running python.
    """

    bits = Enum([32, 64])
    """
    Actual architecture bits (e.g. 32). The architecture is guessed from the
    running python.
    """

    @classmethod
    def from_name(cls, name):
        return cls(name, _ARCH_NAME_TO_BITS[name])

    @classmethod
    def from_running_python(cls):
        return _guess_architecture()

    @classmethod
    def from_running_system(cls):
        return _guess_machine()

    def __init__(self, name, bits):
        super(Arch, self).__init__(name=name, bits=bits)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        else:
            return self.name == other.name and self.bits == other.bits

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.name, self.bits))


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
        return _guess_platform()

    @classmethod
    def from_running_system(cls, arch_string=None):
        return _guess_platform(arch_string)

    def __str__(self):
        return "{0} {1.release} on {1.machine}".format(
            NAME_TO_PRETTY_NAMES[self.name],
            self
        )

    @property
    def _epd_platform_string(self):
        def _append_bits(base):
            if self.arch.name == X86:
                return base + "-32"
            elif self.arch.name == X86_64:
                return base + "-64"
            else:
                msg = ("Unsupported arch in {0.name}: {0.arch.name!r}".
                       format(self))
                raise OkonomiyakiError(msg)

        if self.os == WINDOWS:
            return _append_bits("win")
        elif self.os == DARWIN:
            return _append_bits("osx")
        elif self.os == LINUX:
            if self.family == RHEL:
                parts = self.release.split(".")
                if parts[0] == "3":
                    base = "rh3"
                elif parts[0] == "5":
                    base = "rh5"
                elif parts[0] == "6":
                    base = "rh6"
                else:
                    msg = ("Unsupported rhel release: {0!r}".
                           format(self.release))
                    raise OkonomiyakiError(msg)
                return _append_bits(base)
            else:
                msg = ("Unsupported distribution: {0!r}".
                       format(self.family))
                raise OkonomiyakiError(msg)
        else:
            msg = "Unsupported OS: {0!r}".format(self.name)
            raise OkonomiyakiError(msg)

    @property
    def epd_platform(self):
        return EPDPlatform.from_epd_string(self._epd_platform_string)

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


def _guess_architecture():
    """
    Returns the architecture of the running python.
    """
    bits = platform.architecture()[0]
    machine = platform.machine()
    if machine in ("AMD64", "x86_64"):
        if bits == "32bit":
            return Arch.from_name(X86)
        elif bits == "64bit":
            return Arch.from_name(X86_64)
    elif machine in ("x86", "i386", "i686") and bits == "32bit":
        return Arch.from_name(X86)
    elif platform.system() == 'Darwin' and \
         machine == "i386" and bits == "64bit":  # Yes, this is possible on OSX
        return Arch.from_name(X86_64)
    else:
        raise OkonomiyakiError("Unknown bits/machine combination {0}/{1}".
                               format(bits, machine))


def _guess_machine():
    """
    Returns the underlying machine.
    """
    machine = platform.machine()
    if machine in ("AMD64", "x86_64"):
        return Arch.from_name(X86_64)
    elif machine in ("x86", "i386", "i686"):
        return Arch.from_name(X86)
    else:
        raise OkonomiyakiError("Unknown machine: {0}".  format(machine))


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
        arch = _guess_architecture()
    else:
        arch = Arch.from_name(arch_string)

    machine = _guess_machine()
    os = _guess_os()
    name, family, release = _guess_platform_details(os)

    return Platform(os=os, name=name, family=family, release=release,
                    arch=arch, machine=machine)
