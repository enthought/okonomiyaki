from __future__ import absolute_import

from ..bundled.traitlets import HasTraits, Bool, Enum, Instance, List, Unicode
from ..errors import OkonomiyakiError

from .epd_platform import EPDPlatform
from .platform import DARWIN, LINUX, SOLARIS, WINDOWS
from .platform import CENTOS, RHEL, DEBIAN, UBUNTU, MAC_OS_X
from .platform import Arch


class PlatformLabel(HasTraits):
    """
    A platform filter.
    """

    os = Enum([WINDOWS, LINUX, DARWIN, SOLARIS, None])
    """
    The most generic OS description
    """

    name = Enum([WINDOWS, CENTOS, RHEL, DEBIAN, UBUNTU, MAC_OS_X, SOLARIS,
                 None])
    """
    The most specific platform description
    """

    family = Enum([WINDOWS, RHEL, DEBIAN, MAC_OS_X, SOLARIS, None])
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
    Actual architecture. May be None.
    """

    @classmethod
    def _from_legacy_string(cls, s):
        """ Create a filter from a simple pisi string, e.g. '64', 'win-32' or
        'all'.
        """
        def _epd_name_to_quadruplet(name):
            if name == "rh":
                return (LINUX, RHEL, RHEL, "")
            else:
                platform = EPDPlatform.from_epd_string(name + "-32").platform
                return (platform.os, platform.name, platform.family,
                        platform.release)

        parts = s.split("-")
        if len(parts) == 2:
            name, bits = parts
            arch = Arch._from_bitwidth(bits)
            os, name, family, release = _epd_name_to_quadruplet(name)
            return cls(os, name, family, arch, release)
        elif len(parts) == 1:
            name = parts[0]
            if parts[0] == "all":
                return cls()
            elif parts[0] in ("32", "64"):
                arch = Arch._from_bitwidth(parts[0])
                return cls(arch=arch)
            else:
                arch = None
                os, name, family, release = _epd_name_to_quadruplet(name)
                return cls(os, name, family, arch, release)
        else:
            msg = "Invalid epd string: {0!r}".format(s)
            raise OkonomiyakiError(msg)

    def __init__(self, os=None, name=None, family=None, arch=None, release=""):
        super(PlatformLabel, self).__init__(os=os, name=name, family=family,
                                            arch=arch, release=release)

    def matches(self, platform):
        """ Returns True if the given platform matches this label."""
        if self.os and platform.os != self.os:
            return False

        if self.family and platform.family != self.family:
            return False

        if self.name and platform.name != self.name:
            return False

        if self.release and platform.release != self.release:
            return False

        if self.arch and platform.arch != self.arch:
            return False

        return True


class PlatformLiteral(HasTraits):
    label = Instance(PlatformLabel)
    is_true = Bool(True)

    def __init__(self, label, is_true=True):
        super(PlatformLiteral, self).__init__(label=label, is_true=is_true)


class PlatformFilter(HasTraits):
    platform_labels = List(Instance(PlatformLiteral))

    @classmethod
    def from_legacy_string(cls, s):
        """ Create a filter from a legacy pisi string, e.g. `!win'.
        """
        parts = [p.strip() for p in s.split(",")]
        literals = []
        for part in parts:
            if part.startswith("!"):
                label = PlatformLabel._from_legacy_string(part[1:])
                literal = PlatformLiteral(label, False)
            else:
                label = PlatformLabel._from_legacy_string(part)
                literal = PlatformLiteral(label, True)
            literals.append(literal)

        return cls(literals)

    def __init__(self, labels):
        super(PlatformFilter, self).__init__(platform_labels=labels)

    def matches(self, platform):
        for platform_label in self.platform_labels:
            if ((platform_label.is_true
                 and not platform_label.label.matches(platform))
                or
                (not platform_label.is_true
                 and platform_label.label.matches(platform))):
                return False

        return True
