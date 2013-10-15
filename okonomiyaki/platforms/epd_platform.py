import platform
import sys

from ..bundled.traitlets import HasTraits, Enum
from ..errors import OkonomiyakiError

# Those lists are redundant with legacy spec. We check the consistency in our
# unit-tests
_ARCHBITS_TO_ARCH = {
    "32": "x86",
    "64": "amd64",
}

PLATFORM_NAMES = [
    "osx",
    "rh3",
    "rh5",
    "rh6",
    "sol",
    "win",
]

EPD_PLATFORM_SHORT_NAMES = [
    "osx-32",
    "osx-64",
    "rh3-32",
    "rh3-64",
    "rh5-32",
    "rh5-64",
    "rh6-64",
    "sol-32",
    "sol-64",
    "win-32",
    "win-64",
]


class EPDPlatform(HasTraits):
    """
    An sane Canopy/EPD platform representation.

    Example::

        epd_platform = EPDPlatform.from_epd_string("rh5-32")
        assert epd.platform == "rh5"
        assert epd.arch_bits == "32"
        assert epd.arch == "x86"
    """
    platform = Enum(PLATFORM_NAMES)
    """
    Main name of the platform (e.g. 'rh5')
    """
    arch = Enum(["x86", "amd64"])
    """
    Actual architecture (e.g. 'x86')
    """

    @classmethod
    def from_running_system(cls, arch=None):
        """
        Attempt to create an EPDPlatform instance by guessing the running
        platform. May raise an OkonomiyakiError exception

        Parameters
        ----------
        arch: str, None
            If given, must be a valid architecture string (e.g. 'x86'). If
            None, will be guessed from the running python.
        """
        return _guess_epd_platform(arch)

    @classmethod
    def from_epd_string(cls, s):
        """
        Create a new instance from an epd platform string (e.g. 'win-32')
        """
        parts = s.split("-")
        if len(parts) != 2:
            raise OkonomiyakiError("Invalid epd string: {0}".format(s))

        platform_name, arch_bits = parts
        if not arch_bits in _ARCHBITS_TO_ARCH:
            raise OkonomiyakiError("Invalid epd string (invalid arch): {0}".
                                   format(s))
        else:
            arch = _ARCHBITS_TO_ARCH[arch_bits]

        return cls(platform_name, arch)

    def __init__(self, platform, arch, **kw):
        super(EPDPlatform, self).__init__(platform=platform, arch=arch, **kw)

    @property
    def arch_bits(self):
        """
        The number of bits (as a string) of this epd platform.
        """
        if self.arch == "x86":
            return "32"
        else:
            return "64"

    @property
    def short(self):
        return "{0}-{1}".format(self.platform, self.arch_bits)


def _guess_architecture():
    """
    Returns the architecture of the running python.
    """
    x86 = "x86"
    amd64 = "amd64"
    bits = platform.architecture()[0]
    machine = platform.machine()
    if machine in ("AMD64", "x86_64"):
        if bits == "32bit":
            return x86
        elif bits == "64bit":
            return amd64
    elif machine in ("x86", "i386", "i686") and bits == "32bit":
        return x86
    else:
        raise OkonomiyakiError("Unknown bits/machine combination {0}/{1}".
                               format(bits, machine))


def _guess_epd_platform(arch=None):
    if arch is None:
        arch = _guess_architecture()

    if sys.platform == "win32":
        return EPDPlatform("win", arch)
    elif sys.platform == "darwin":
        return EPDPlatform("osx", arch)
    elif sys.platform.startswith("linux"):
        name, version, _ = platform.dist()
        if name in ("centos", "redhat"):
            parts = version.split(".")
            if not len(parts) == 2:
                raise OkonomiyakiError("Could not parse rh version {0}".
                                       format(version))
            major, _ = parts
            if major == "5":
                return EPDPlatform("rh5", arch)
            elif major == "6":
                return EPDPlatform("rh6", arch)
            else:
                raise OkonomiyakiError("Unknown major version {0}".
                                       format(major))
        else:
            raise OkonomiyakiError("Could not guess platform for distribution "
                                   "{0}".format(name))
    else:
        raise OkonomiyakiError("Could not guess epd platform")
