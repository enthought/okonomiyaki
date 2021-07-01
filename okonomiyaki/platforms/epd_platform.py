from __future__ import absolute_import

import re
import warnings

import six

from attr import attributes, attr
from attr.validators import instance_of

from okonomiyaki.versions import RuntimeVersion
from okonomiyaki.errors import OkonomiyakiError, InvalidPEP440Version
from ._arch import Arch, ArchitectureKind
from ._platform import OSKind, FamilyKind, NameKind, Platform

# the string used in EGG-INFO/spec/depend. Only used during normalization
# operations.
_X86_64_LEGACY_SPEC = "amd64"

# Those lists are redundant with legacy spec. We check the consistency in our
# unit-tests
_ARCHBITS_TO_ARCH = {
    "32": ArchitectureKind.x86.name,
    "64": _X86_64_LEGACY_SPEC,
    ArchitectureKind.x86: ArchitectureKind.x86.name,
    ArchitectureKind.x86_64: _X86_64_LEGACY_SPEC,
}

X86 = Arch(ArchitectureKind.x86)
X86_64 = Arch(ArchitectureKind.x86_64)

PLATFORM_NAMES = (
    "osx",
    "rh3",
    "rh5",
    "rh6",
    "rh7",
    "sol",
    "win",
)

EPD_PLATFORM_SHORT_NAMES = (
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
)

VALID_PLATFORMS_FILTER = PLATFORM_NAMES + ("all", "rh",)

_EPD_PLATFORM_STRING_RE = re.compile(r"""
    ^
    (?P<os>[^-_]+)
    [_-]
    (?P<arch>[^-]+)
    $
    """, flags=re.VERBOSE)

_LINUX_TAG_R = re.compile(r"^linux_(?P<arch>\S+)$")
_MACOSX_TAG_R = re.compile(r"^macosx_([^_]+)_([^_]+)_(?P<arch>\S+)$")
_WINDOWS_TAG_R = re.compile(r"^win_*(?P<arch>\S+)$")

_ANY_PLATFORM_STRING = u'any'


def platform_validator():
    def wrapper(inst, attr, value):
        instance_of(Platform)(inst, attr, value)
        if not _is_supported(value):
            raise OkonomiyakiError(
                "Platform {0} not supported".format(value)
            )
    return wrapper


@six.python_2_unicode_compatible
@attributes(frozen=True)
class EPDPlatform(object):
    """
    An sane Canopy/EPD platform representation.

    Example::

        epd_platform = EPDPlatform.from_epd_string("rh5-32")
        assert epd.name == "rh5"
        assert epd.arch_bits == "32"
        assert epd.arch == "x86"
    """

    platform = attr(validator=platform_validator())
    """
    Main name of the platform (e.g. 'rh5')
    """

    @staticmethod
    def pep425_tag_string(platform):
        if platform is None:
            return _ANY_PLATFORM_STRING
        else:
            return platform.pep425_tag

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
    def from_string(cls, s, runtime_version=None):
        """ Create a new instance from an epd platform string.

        Parameters:
        s : string
           The platform string e.g. win-32. New, more explicit
           architecture names are also supported, e.g. 'win-x86' or
           'win-x86_64' are supported.
        runtime_version: RuntimeVersion
           Passing the runtime version will result in more precise Platform
           description taking into account the historical records of the
           Enthought python runtime releases.
        """
        m = _EPD_PLATFORM_STRING_RE.match(s)
        if m is None:
            raise OkonomiyakiError("Invalid epd string: {0}".format(s))
        else:
            d = m.groupdict()
            platform_name = d["os"]
            arch_bits = d["arch"]
            if arch_bits not in _ARCHBITS_TO_ARCH:
                arch = machine = Arch.from_name(arch_bits)
            else:
                arch_name = _ARCHBITS_TO_ARCH[arch_bits]
                arch = machine = Arch.from_name(arch_name)
            os, name, family, release = _epd_name_and_python_to_quadruplet(
                platform_name, runtime_version)
            platform = Platform(os, name, family, release, arch, machine)
            return cls(platform)

    @classmethod
    def from_epd_string(cls, s, runtime_version=None):
        """
        Create a new instance from an epd platform string (e.g. 'win-32')

        DEPRECATED: use from_string instead.
        """
        warnings.warn(
            "Deprecated: use EPDPlatform.from_string instead",
            DeprecationWarning
        )
        return cls.from_string(s, runtime_version)

    @classmethod
    def _from_spec_depend_data(
            cls, platform, osdist, arch_name,
            platform_tag, python_version, platform_abi):
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

        if python_version is not None:
            try:
                python_version = RuntimeVersion.from_string(python_version)
            except InvalidPEP440Version:
                python_version = None

        os_kind, name_kind, family_kind, release = _epd_name_and_python_to_quadruplet(
            epd_name, python_version)

        if 'osx' in platform_tag.lower():
            release = '.'.join(platform_tag.split('_')[1:3])

        platform = Platform(
            os_kind=os_kind, name_kind=name_kind, family_kind=family_kind,
            release=release, arch=arch, machine=arch)
        return cls(platform)

    @classmethod
    def _from_platform_tag(cls, platform_tag):
        """
        Attempt to create an EPDPlatform instance from a PEP 425 platform tag.
        """
        if platform_tag is None or platform_tag == _ANY_PLATFORM_STRING:
            raise ValueError(
                "Invalid platform_tag for platform: '{}'".format(platform_tag)
            )
        else:
            if platform_tag.startswith("linux"):
                m = _LINUX_TAG_R.match(platform_tag)
                assert m, platform_tag
                arch_string = m.group("arch")
                epd_string = u"rh5_" + str(Arch.from_name(arch_string))
            elif platform_tag.startswith("macosx"):
                m = _MACOSX_TAG_R.match(platform_tag)
                assert m, platform_tag
                arch_string = m.group("arch")
                epd_string = u"osx_" + str(Arch.from_name(arch_string))
            elif platform_tag.startswith("win"):
                m = _WINDOWS_TAG_R.match(platform_tag)
                assert m, platform_tag
                arch_string = m.group("arch")
                if arch_string == "32":
                    epd_string = u"win_i386"
                else:
                    epd_string = u"win_" + str(Arch.from_name(arch_string))
            else:
                raise NotImplementedError(
                    "Unsupported platform '{0}'".format(platform_tag)
                )

            return cls.from_epd_string(epd_string)

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

        platform = self.platform
        if platform.os_kind == OSKind.darwin:
            release = platform.release.replace('.', '_')
            if platform.arch == X86:
                return u"macosx_{}_i386".format(release)
            elif platform.arch == X86_64:
                return u"macosx_{}_x86_64".format(release)
            else:
                raise OkonomiyakiError(msg.format(platform))
        elif platform.os_kind == OSKind.linux:
            if platform.arch == X86:
                return u"linux_i686"
            elif platform.arch == X86_64:
                return u"linux_x86_64"
            else:
                raise OkonomiyakiError(msg.format(platform))
        elif platform.os_kind == OSKind.windows:
            if platform.arch == X86:
                return u"win32"
            elif platform.arch == X86_64:
                return u"win_amd64"
            else:
                raise OkonomiyakiError(msg.format(platform))
        else:
            raise OkonomiyakiError(msg.format(platform))

    @property
    def platform_name(self):
        os_kind = self.platform.os_kind
        if os_kind == OSKind.windows:
            return u"win"
        elif os_kind == OSKind.darwin:
            return u"osx"
        elif os_kind == OSKind.linux:
            family_kind = self.platform.family_kind
            release = self.platform.release
            if family_kind == FamilyKind.rhel:
                parts = release.split(".")
                if parts[0] == "3":
                    base = u"rh3"
                elif parts[0] == "5":
                    base = u"rh5"
                elif parts[0] == "6":
                    base = u"rh6"
                elif parts[0] == "7":
                    base = u"rh7"
                else:
                    msg = ("Unsupported rhel release: {0!r}".format(release))
                    raise OkonomiyakiError(msg)
                return base
            else:
                msg = "Unsupported distribution: {0!r}".format(family_kind)
                raise OkonomiyakiError(msg)
        elif os_kind == OSKind.solaris:
            return u"sol"
        else:
            msg = "Unsupported OS: {0!r}".format(self.platform.name)
            raise OkonomiyakiError(msg)

    @property
    def short(self):
        return u"{0}-{1}".format(self.platform_name, self.arch_bits)

    def __str__(self):
        return u"{0.platform_name}_{0.arch}".format(self)

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
            if parts[0] in VALID_PLATFORMS_FILTER:
                return parts[0], None
            elif parts[0] in _ARCHBITS_TO_ARCH:
                return "all", parts[0]
            else:
                raise ValueError(
                    "Invalid filter string: '{}'".format(component)
                )
        elif len(parts) == 2:
            if (
                parts[0] not in VALID_PLATFORMS_FILTER
                or parts[1] not in _ARCHBITS_TO_ARCH
            ):
                raise ValueError(
                    "Invalid filter string: '{}'".format(component)
                )
            return parts[0], parts[1]
        else:
            raise ValueError(
                "Invalid filter string: '{}'".format(component)
            )

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
    else:
        to_platform = to.platform_name
        to_arch_bits = to.arch_bits

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


def _epd_name_and_python_to_quadruplet(name, runtime_version=None):
    py38 = RuntimeVersion.from_string('3.8')
    if name == "rh7":
        return (OSKind.linux, NameKind.rhel, FamilyKind.rhel, "7.1")
    if name == "rh6":
        return (OSKind.linux, NameKind.rhel, FamilyKind.rhel, "6.5")
    elif name == "rh5":
        return (OSKind.linux, NameKind.rhel, FamilyKind.rhel, "5.8")
    elif name == "rh3":
        return (OSKind.linux, NameKind.rhel, FamilyKind.rhel, "3.8")
    elif name == "osx":
        if runtime_version is not None and runtime_version >= py38:
            return (OSKind.darwin, NameKind.mac_os_x, FamilyKind.mac_os_x, "10.14")
        else:
            return (OSKind.darwin, NameKind.mac_os_x, FamilyKind.mac_os_x, "10.6")
    elif name == "sol":
        return (OSKind.solaris, NameKind.solaris, FamilyKind.solaris, "")
    elif name == "win":
        if runtime_version is not None and runtime_version >= py38:
            return (OSKind.windows, NameKind.windows, FamilyKind.windows, "10")
        else:
            return (OSKind.windows, NameKind.windows, FamilyKind.windows, "")
    else:
        msg = "Invalid epd platform string name: {0!r}".format(name)
        raise OkonomiyakiError(msg)


def _guess_epd_platform(arch=None):
    if arch is None:
        arch = Arch.from_running_python()

    platform = Platform.from_running_system(str(arch))
    return EPDPlatform(platform)


def _is_supported(platform):
    arch_and_machine_are_intel = (
        platform.arch in (X86, X86_64)
        and platform.machine in (X86, X86_64)
    )
    if platform.os_kind == OSKind.windows:
        return arch_and_machine_are_intel
    if platform.os_kind == OSKind.darwin:
        return arch_and_machine_are_intel
    if platform.os_kind == OSKind.solaris:
        return arch_and_machine_are_intel
    if platform.os_kind == OSKind.linux:
        if platform.family_kind != FamilyKind.rhel:
            return False
        parts = platform.release.split(".")
        return parts[0] in ("3", "5", "6", "7") \
            and arch_and_machine_are_intel

    return False
