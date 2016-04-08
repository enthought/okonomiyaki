from __future__ import absolute_import

import platform
import sys

import enum

from attr import attr, attributes
from attr.validators import instance_of

from ..errors import OkonomiyakiError


@enum.unique
class ArchitectureKind(enum.Enum):
    x86 = 0
    x86_64 = 1


_KIND_TO_BITWIDTHS = {
    ArchitectureKind.x86: 32,
    ArchitectureKind.x86_64: 64,
}
for k in ArchitectureKind.__members__:
    assert ArchitectureKind[k] in _KIND_TO_BITWIDTHS

_NORMALIZED_NAMES = {
    "x86": ArchitectureKind.x86,
    "i386": ArchitectureKind.x86,
    "i686": ArchitectureKind.x86,

    "amd64": ArchitectureKind.x86_64,
    "AMD64": ArchitectureKind.x86_64,
    "x86_64": ArchitectureKind.x86_64,
}


@attributes
class Arch(object):
    """ A normalized architecture representation.
    """
    _kind = attr(validator=instance_of(ArchitectureKind))

    @classmethod
    def _from_bitwidth(cls, bitwidth):
        if bitwidth == "32":
            return cls(ArchitectureKind.x86)
        elif bitwidth == "64":
            return cls(ArchitectureKind.x86_64)
        else:
            msg = "Invalid bits width: {0!r}".format(bitwidth)
            raise OkonomiyakiError(msg)

    @classmethod
    def from_name(cls, name):
        kind = _NORMALIZED_NAMES.get(name)
        if kind is None:
            raise OkonomiyakiError(
                "Unsupported/unrecognized architecture: {0!r}".format(name)
            )
        else:
            return cls(kind)

    @classmethod
    def from_running_python(cls):
        machine = platform.machine()

        if machine in _NORMALIZED_NAMES:
            if sys.maxsize > 2 ** 32:
                return Arch(ArchitectureKind.x86_64)
            else:
                return Arch(ArchitectureKind.x86)
        else:
            raise OkonomiyakiError(
                "Unknown machine combination {0!r}".format(machine)
            )

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
