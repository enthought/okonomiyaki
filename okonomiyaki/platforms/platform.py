from __future__ import absolute_import

import platform
import sys

import enum
import six

from attr import attr, attributes
from attr.validators import instance_of

from ..errors import OkonomiyakiError

from ._arch import Arch


@enum.unique
class OSKind(enum.Enum):
    darwin = 0
    linux = 1
    solaris = 2
    windows = 3


@enum.unique
class FamilyKind(enum.Enum):
    rhel = 0
    debian = 1
    mac_os_x = 2
    windows = 3
    solaris = 4


@enum.unique
class NameKind(enum.Enum):
    centos = 0
    debian = 1
    rhel = 2
    ubuntu = 3
    mac_os_x = 4
    windows = 5
    solaris = 6


NAME_KIND_TO_PRETTY_NAMES = {
    NameKind.windows: "Windows",
    NameKind.mac_os_x: "Mac OS X",
    NameKind.centos: "CentOS",
    NameKind.rhel: "RedHat",
    NameKind.ubuntu: "Ubuntu",
    NameKind.debian: "Debian",
}


@six.python_2_unicode_compatible
@attributes(repr=False)
class Platform(object):
    """
    An generic platform representation.
    """

    os_kind = attr(validator=instance_of(OSKind))
    """
    The most generic OS description
    """

    name_kind = attr(validator=instance_of(NameKind))
    """
    The most specific platform description
    """

    family_kind = attr(validator=instance_of(FamilyKind))
    """
    The 'kind' of platforms. For example, both debian and ubuntu distributions
    share the same kind, 'debian'.
    """

    release = attr(validator=instance_of(six.string_types))
    """
    The release string. May be an empty string
    """

    arch = attr(validator=instance_of(Arch))
    """
    Actual architecture. The architecture is guessed from the running python.
    """

    machine = attr(validator=instance_of(Arch))
    """
    The machine. This is the CPU architecture (e.g. for a 32 bits python
    running on 64 bits Intel OS, machine will be an x86_64 arch, whereas arch
    will be an 'x86' arch)
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

    @property
    def family(self):
        return self.family_kind.name

    @property
    def name(self):
        return self.name_kind.name

    @property
    def os(self):
        return self.os_kind.name

    def __repr__(self):
        return (
            "Platform(os={0.os!r}, name={0.name!r}, family={0.family!r}, "
            "arch='{0.arch}', machine='{0.machine}')".format(self)
        )

    def __str__(self):
        return u"{0} {1.release} on {1.machine}".format(
            NAME_KIND_TO_PRETTY_NAMES[self.name_kind],
            self
        )


def _guess_os_kind():
    if sys.platform == "win32":
        return OSKind.windows
    elif sys.platform == "darwin":
        return OSKind.darwin
    elif sys.platform.startswith("linux"):
        return OSKind.linux
    else:
        msg = "Could not guess platform from sys.platform: {0!r}"
        raise OkonomiyakiError(msg.format(sys.platform))


def _guess_platform_details(os_kind):
    if os_kind == OSKind.windows:
        return FamilyKind.windows, NameKind.windows, platform.win32_ver()[0]
    elif os_kind == OSKind.darwin:
        return FamilyKind.mac_os_x, NameKind.mac_os_x, platform.mac_ver()[0]
    elif os_kind == OSKind.linux:
        name = platform.linux_distribution()[0].lower()
        _, release, _ = platform.dist()
        try:
            name_kind = NameKind[name]
        except KeyError:
            raise OkonomiyakiError(
                "Unsupported platform: {0!r}".format(name)
            )
        else:
            if name_kind in (NameKind.ubuntu, NameKind.debian):
                family_kind = FamilyKind.debian
            elif name_kind in (NameKind.centos, NameKind.rhel):
                family_kind = FamilyKind.rhel
            else:
                raise OkonomiyakiError("Unsupported platform: {0!r}".format(name))
            return family_kind, name_kind, release


def _guess_platform(arch_string=None):
    if arch_string is None:
        arch = Arch.from_running_python()
    else:
        arch = Arch.from_name(arch_string)

    machine = Arch.from_running_system()
    os_kind = _guess_os_kind()
    family_kind, name_kind, release = _guess_platform_details(os_kind)

    return Platform(os_kind, name_kind, family_kind, release, arch, machine)
