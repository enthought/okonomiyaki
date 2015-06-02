from __future__ import absolute_import

import platform

from ..bundled.traitlets import HasTraits, Enum
from ..errors import OkonomiyakiError

from . import epd_platform


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

    bits = Enum([32, 64])
    """
    Actual architecture bits (e.g. 32). The architecture is guessed from the
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
        normalized_name = _ARCH_NAME_TO_NORMALIZED.get(name)
        if normalized_name is None:
            msg = "Unsupported/unrecognized architecture: {0!r}"
            raise OkonomiyakiError(msg.format(name))
        return cls(normalized_name, _ARCH_NAME_TO_BITS[normalized_name])

    @classmethod
    def from_running_python(cls):
        return _guess_architecture()

    @classmethod
    def from_running_system(cls):
        return Arch.from_name(platform.machine())

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


def _guess_architecture():
    """
    Returns the architecture of the running python.
    """
    epd_platform_arch = epd_platform._guess_architecture()
    if epd_platform_arch == "x86":
        return Arch.from_name(X86)
    elif epd_platform_arch == "amd64":
        return Arch.from_name(X86_64)
    else:
        raise OkonomiyakiError("Unknown architecture {0!r}".
                               format(epd_platform_arch))
