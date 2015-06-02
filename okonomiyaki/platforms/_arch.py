from __future__ import absolute_import

import platform
import sys

from ..bundled.traitlets import HasTraits, Enum
from ..errors import OkonomiyakiError


X86 = "x86"
X86_64 = "x86_64"

_ARCH_NAME_TO_BITS = {
    X86: 32,
    X86_64: 64,
}

_ARCH_NAME_TO_NORMALIZED = {
    "amd64": X86_64,
    "AMD64": X86_64,
    "x86_64": X86_64,
    "x86": X86,
    "i386": X86,
    "i686": X86,
}


class Arch(HasTraits):
    name = Enum([X86, X86_64])
    """
    Actual architecture name (e.g. 'x86'). The architecture is guessed from the
    running python.
    """

    @classmethod
    def _from_bitwidth(cls, bitwidth):
        if bitwidth == "32":
            return cls.from_name(X86)
        elif bitwidth == "64":
            return cls.from_name(X86_64)
        else:
            msg = "Invalid bits width: {0!r}".format(bitwidth)
            raise OkonomiyakiError(msg)

    @classmethod
    def from_name(cls, name):
        # FIXME: kept for backward compatibility
        return cls(name)

    @classmethod
    def from_running_python(cls):
        machine = platform.machine()

        if machine in _ARCH_NAME_TO_NORMALIZED:
            if sys.maxsize > 2 ** 32:
                return Arch.from_name(X86_64)
            else:
                return Arch.from_name(X86)
        else:
            raise OkonomiyakiError("Unknown machine combination {0!r}".
                                   format(machine))

    @classmethod
    def from_running_system(cls):
        return Arch.from_name(platform.machine())

    def __init__(self, name):
        normalized_name = _ARCH_NAME_TO_NORMALIZED.get(name)
        if normalized_name is None:
            msg = "Unsupported/unrecognized architecture: {0!r}"
            raise OkonomiyakiError(msg.format(name))

        super(Arch, self).__init__(name=normalized_name)

    @property
    def bits(self):
        """
        Actual architecture bits (e.g. 32), as an int.
        """
        return _ARCH_NAME_TO_BITS[self.name]

    @property
    def _arch_bits(self):
        # Used by EPDPlatform
        return str(self.bits)

    @property
    def _legacy_name(self):
        # Used for translating the arch into EGG-INFO/spec/depend (old
        # 'platform' entry)
        if self.name == X86_64:
            return "amd64"
        else:
            return self.name

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
