from __future__ import absolute_import

import re

from ..bundled.traitlets import HasTraits, Instance
from ..errors import OkonomiyakiError
from ._arch import Arch, X86_64, X86
from .platform import (
    Platform, DARWIN, LINUX, MAC_OS_X, RHEL, SOLARIS, WINDOWS
)

# the string used in EGG-INFO/spec/depend. Only used during normalization
# operations.
_X86_64_LEGACY_SPEC = "amd64"

# Those lists are redundant with legacy spec. We check the consistency in our
# unit-tests
_ARCHBITS_TO_ARCH = {
    "32": X86,
    "64": _X86_64_LEGACY_SPEC,
    X86: X86,
    X86_64: _X86_64_LEGACY_SPEC,
}

PLATFORM_NAMES = [
    "osx",
    "rh3",
    "rh5",
    "rh6",
    "rh7",
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
    "rh7-64",
    "sol-32",
    "sol-64",
    "win-32",
    "win-64",
]

_X86 = Arch.from_name(X86)
_X64_64 = Arch.from_name(X86_64)


_EPD_PLATFORM_STRING_RE = re.compile("""
    (?P<os>[^-_]+)
    [_-]
    (?P<arch>[^-]+)
    """, flags=re.VERBOSE)


class EPDPlatform(HasTraits):
    """
    An sane Canopy/EPD platform representation.

    Example::

        epd_platform = EPDPlatform.from_epd_string("rh5-32")
        assert epd.name == "rh5"
        assert epd.arch_bits == "32"
        assert epd.arch == "x86"
    """

    platform = Instance(Platform)
    """
    Main name of the platform (e.g. 'rh5')
    """

    @classmethod
    def from_running_python(cls):
        """
        Attempt to create an EPDPlatform instance by guessing the running
        python. May raise an OkonomiyakiError exception
        """
        return cls(Platform.from_running_python())

    @classmethod
    def from_running_system(cls, arch_name=None):
        """
        Attempt to create an EPDPlatform instance by guessing the running
        platform. May raise an OkonomiyakiError exception

        Parameters
        ----------
        arch_name: str, None
            If given, must be a valid architecture string (e.g. 'x86'). If
            None, will be guessed from the running platform.
        """
        if arch_name is not None:
            arch = Arch.from_name(arch_name)
        else:
            arch = Arch.from_running_system()
        return _guess_epd_platform(arch)

    @classmethod
    def from_epd_string(cls, s):
        """
        Create a new instance from an epd platform string (e.g. 'win-32')

        Note: new, more explicit architecture names are also supported, e.g.
        'win-x86' or 'win-x86_64' are supported.
        """
        m = _EPD_PLATFORM_STRING_RE.match(s)
        if m is None:
            raise OkonomiyakiError("Invalid epd string: {0}".format(s))
        else:
            d = m.groupdict()
            platform_name = d["os"]
            arch_bits = d["arch"]
            if arch_bits not in _ARCHBITS_TO_ARCH:
                arch = machine = Arch(arch_bits)
            else:
                arch_name = _ARCHBITS_TO_ARCH[arch_bits]
                arch = machine = Arch(arch_name)
            os, name, family, release = _epd_name_to_quadruplet(platform_name)
            platform = Platform(os, name, family, arch, machine, release)
            return cls(platform)

    @classmethod
    def _from_spec_depend_data(cls, platform, osdist, arch_name):
        msg = ("Unrecognized platform/osdist combination: {0!r}/{1!r}"
               .format(platform, osdist))

        arch = Arch.from_name(arch_name)
        if platform == "darwin":
            epd_name = "osx"
        elif platform == "win32":
            epd_name = "win"
        elif platform.startswith("linux"):
            if osdist == "RedHat_3":
                epd_name = "rh3"
            elif osdist in (None, "RedHat_5"):
                epd_name = "rh5"
            elif osdist == "RedHat_6":
                epd_name = "rh6"
            elif osdist == "RedHat_7":
                epd_name = "rh7"
            else:
                raise ValueError(msg)
        else:
            raise ValueError(msg)
        return cls.from_epd_string("{0}-{1}".format(epd_name, arch._arch_bits))

    def __init__(self, platform, **kw):
        if not self._is_supported(platform):
            msg = "Platform {0} not supported".format(platform)
            raise OkonomiyakiError(msg)
        super(EPDPlatform, self).__init__(platform=platform, **kw)

    def _is_supported(self, platform):
        arch_and_machine_are_intel = (
            platform.arch in (_X86, _X64_64)
            and platform.machine in (_X86, _X64_64)
        )
        if platform.os == WINDOWS:
            return arch_and_machine_are_intel
        if platform.os == DARWIN:
            return arch_and_machine_are_intel
        if platform.os == SOLARIS:
            return arch_and_machine_are_intel
        if platform.os == LINUX:
            if platform.family != RHEL:
                return False
            parts = platform.release.split(".")
            return parts[0] in ("3", "5", "6", "7") \
                and arch_and_machine_are_intel

        return False

    @property
    def arch(self):
        return self.platform.arch

    @property
    def arch_bits(self):
        """
        The number of bits (as a string) of this epd platform.
        """
        return self.arch._arch_bits

    @property
    def pep425_tag(self):
        msg = "Cannot guess platform tag for platform {0!r}"

        if self.platform.family == MAC_OS_X:
            if self.platform.arch.name == X86:
                return "macosx_10_6_i386"
            elif self.platform.arch.name == X86_64:
                return "macosx_10_6_x86_64"
            else:
                raise OkonomiyakiError(msg.format(self.platform))
        elif self.platform.os == LINUX:
            if self.platform.arch.name == X86:
                return "linux_i686"
            elif self.platform.arch.name == X86_64:
                return "linux_x86_64"
            else:
                raise OkonomiyakiError(msg.format(self.platform))
        elif self.platform.family == WINDOWS:
            if self.platform.arch.name == X86:
                return "win32"
            elif self.platform.arch.name == X86_64:
                return "win_amd64"
            else:
                raise OkonomiyakiError(msg.format(self.platform))
        else:
            raise OkonomiyakiError(msg.format(self.platform))

    @property
    def platform_name(self):
        os = self.platform.os
        if os == WINDOWS:
            return "win"
        elif os == DARWIN:
            return "osx"
        elif os == LINUX:
            family = self.platform.family
            release = self.platform.release
            if family == RHEL:
                parts = release.split(".")
                if parts[0] == "3":
                    base = "rh3"
                elif parts[0] == "5":
                    base = "rh5"
                elif parts[0] == "6":
                    base = "rh6"
                elif parts[0] == "7":
                    base = "rh7"
                else:
                    msg = ("Unsupported rhel release: {0!r}".format(release))
                    raise OkonomiyakiError(msg)
                return base
            else:
                msg = "Unsupported distribution: {0!r}".format(family)
                raise OkonomiyakiError(msg)
        elif os == SOLARIS:
            return "sol"
        else:
            msg = "Unsupported OS: {0!r}".format(self.platform.name)
            raise OkonomiyakiError(msg)

    @property
    def short(self):
        return "{0}-{1}".format(self.platform_name, self.arch_bits)

    def __str__(self):
        return "{0.platform_name}_{0.arch}".format(self)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.platform == other.platform

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return True
        return not (self.platform == other.platform)

    def __hash__(self):
        return hash(self.platform)


def applies(platform_string, to='current'):
    """ Returns True if the given platform string applies to the platform
    specified by 'to'."""
    def _parse_component(component):
        component = component.strip()

        parts = component.split("-")
        if len(parts) == 1:
            return parts[0], None
        elif len(parts) == 2:
            return parts[0], parts[1]
        else:
            raise ValueError()

    def _are_compatible(short_left, short_right):
        return short_left == short_right or \
            short_left == "rh" and short_right.startswith("rh") \
            or short_right == "rh" and short_left.startswith("rh") \
            or short_left == "all"

    if isinstance(to, str):
        if to == 'current':
            full = EPDPlatform.from_running_system()
            to_platform = full.platform_name
            to_arch_bits = full.arch_bits
        elif '-' in to:
            full = EPDPlatform.from_epd_string(to)
            to_platform = full.platform_name
            to_arch_bits = full.arch_bits
        else:
            if not (to in PLATFORM_NAMES or to == 'rh'):
                raise ValueError("Invalid 'to' argument: {0!r}".format(to))
            to_platform = to
            to_arch_bits = None

    conditions = []

    platform_string = platform_string.strip()
    if platform_string.startswith("!"):
        invert = True
        platform_string = platform_string[1:]
    else:
        invert = False

    platform_strings = [s for s in platform_string.split(",")]
    for platform_string in platform_strings:
        short, bits = _parse_component(platform_string)
        if _are_compatible(short, to_platform):
            if bits is None:
                conditions.append(True)
            else:
                conditions.append(bits == to_arch_bits or to_arch_bits is None)
        else:
            conditions.append(False)

    if invert:
        return not any(conditions)
    else:
        return any(conditions)


def _epd_name_to_quadruplet(name):
    if name == "rh7":
        return (LINUX, RHEL, RHEL, "7.1")
    if name == "rh6":
        return (LINUX, RHEL, RHEL, "6.5")
    elif name == "rh5":
        return (LINUX, RHEL, RHEL, "5.8")
    elif name == "rh3":
        return (LINUX, RHEL, RHEL, "3.8")
    elif name == "osx":
        return (DARWIN, MAC_OS_X, MAC_OS_X, "10.6")
    elif name == "sol":
        return (SOLARIS, SOLARIS, SOLARIS, "")
    elif name == "win":
        return (WINDOWS, WINDOWS, WINDOWS, "")
    else:
        msg = "Invalid epd platform string name: {0!r}".format(name)
        raise OkonomiyakiError(msg)


def _guess_epd_platform(arch=None):
    if arch is None:
        arch = Arch.from_running_python()

    platform = Platform.from_running_system(str(arch))
    return EPDPlatform(platform)
