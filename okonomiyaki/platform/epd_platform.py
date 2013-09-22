from okonomiyaki.errors import OkonomiyakiError
from okonomiyaki.bundled.traitlets import HasTraits, Enum

# Those lists are redundant with legacy spec. We check the consistency in our
# unit-tests
_ARCHBITS_TO_ARCH= {
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
    arch = Enum(["x86", "amd64"])

    @classmethod
    def from_epd_string(cls, s):
        """
        Create a new instance from an epd platform string (e.g. 'win-32')
        """
        parts = s.split("-")
        if len(parts) != 2:
            raise OkonomiyakiError("Invalid epd string: {0}".format(s))

        platform, arch_bits = parts
        if not arch_bits in _ARCHBITS_TO_ARCH:
            raise OkonomiyakiError("Invalid epd string (invalid arch): {0}".format(s))
        else:
            arch = _ARCHBITS_TO_ARCH[arch_bits]

        return cls(platform, arch)

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
