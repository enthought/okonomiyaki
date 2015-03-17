from __future__ import absolute_import

from okonomiyaki.bundled.traitlets import (HasTraits, Bool, Enum, Instance,
                                           List, Unicode)

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

    def matches(self, platform):
        """ Returns True if the given platform matches this label."""
        if self.os and not platform.os == self.os:
            return False

        if self.family and not platform.family == self.family:
            return False

        if self.name and not platform.name == self.name:
            return False

        if self.release and not platform.release == self.release:
            return False

        if self.arch and not platform.arch == self.arch:
            return False

        return True


class PlatformLiteral(HasTraits):
    label = Instance(PlatformLabel)
    is_true = Bool(True)

    def __init__(self, label, is_true=True):
        super(PlatformLiteral, self).__init__(label=label, is_true=is_true)


class PlatformFilter(HasTraits):
    platform_labels = List(Instance(PlatformLiteral))

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
