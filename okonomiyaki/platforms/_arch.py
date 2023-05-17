from __future__ import absolute_import

import platform
import sys

import enum

from attr import attr, attributes
from attr.validators import instance_of

from okonomiyaki.errors import OkonomiyakiError


@enum.unique
class ArchitectureKind(enum.Enum):
    x86 = 0
    x86_64 = 1
    arm64 = 2


_KIND_TO_BITWIDTHS = {
    ArchitectureKind.x86: 32,
    ArchitectureKind.x86_64: 64,
    ArchitectureKind.arm64: 64}

_64BIT_NAMES = {
    "amd64": ArchitectureKind.x86_64,
    "AMD64": ArchitectureKind.x86_64,
    "x86_64": ArchitectureKind.x86_64,
    "arm64": ArchitectureKind.arm64,
    "ARM64": ArchitectureKind.arm64,
    "aarch64": ArchitectureKind.arm64,
}

_32BIT_NAMES = {
    "x86": ArchitectureKind.x86,
    "i386": ArchitectureKind.x86,
    "i686": ArchitectureKind.x86,
}

_NORMALIZED_NAMES = {}
_NORMALIZED_NAMES.update(_64BIT_NAMES)
_NORMALIZED_NAMES.update(_32BIT_NAMES)


@attributes(frozen=True)
class Arch(object):
    """ A normalized architecture representation.
    """
    _kind = attr(validator=instance_of(ArchitectureKind))

    @classmethod
    def _from_bitwidth(cls, bitwidth):
        if bitwidth == "32":
            return cls(ArchitectureKind.x86)
        elif bitwidth == "64":
            machine = platform.machine()
            return cls(_64BIT_NAMES[machine])
        else:
            msg = "Invalid bits width: {0!r}".format(bitwidth)
            raise OkonomiyakiError(msg)

    @classmethod
    def from_name(cls, name):
        kind = _NORMALIZED_NAMES.get(name)
        if kind is None:
            raise OkonomiyakiError(
                "Unsupported/unrecognized architecture: {0!r}".format(name))
        else:
            return cls(kind)

    @classmethod
    def from_running_python(cls):
        machine = platform.machine()
        if machine not in _NORMALIZED_NAMES:
            raise OkonomiyakiError("Unknown machine type {0!r}".format(machine))
        elif sys.maxsize > 2 ** 32:
            if machine in _64BIT_NAMES:
                return Arch(_64BIT_NAMES[machine])
            else:
                raise OkonomiyakiError("A 64bit python is running on a {0!r}".format(machine))
        else:
            return Arch(ArchitectureKind.x86)


    @classmethod
    def from_running_system(cls):
        return Arch.from_name(platform.machine())

    @property
    def bits(self):
        """
        Actual architecture bits (e.g. 32), as an int.
        """
        return _KIND_TO_BITWIDTHS[self._kind]

    @property
    def name(self):
        """ The normalized architecture name."""
        return self._kind.name

    @property
    def _arch_bits(self):
        # Used by EPDPlatform
        return str(self.bits)

    @property
    def _legacy_name(self):
        # Used for translating the arch into EGG-INFO/spec/depend (old
        # 'platform' entry)
        if self._kind == ArchitectureKind.x86_64:
            return "amd64"
        else:
            return self.name

    def __str__(self):
        return self.name


X86 = Arch(ArchitectureKind.x86)
X86_64 = Arch(ArchitectureKind.x86_64)
ARM64 = Arch(ArchitectureKind.arm64)
