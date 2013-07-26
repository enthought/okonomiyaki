"""Traitlets-based models for egg-related metadata."""
import re

from okonomiyaki.errors import InvalidEggName, InvalidDependencyString

from ..utils.traitlets import HasTraits, Enum, Instance, List, Long, Unicode
from .constants import _PLATFORMS_DESCRIPTIONS, _PLATFORMS_SHORT_NAMES

_EGG_NAME_RE = re.compile("(?P<name>[\w]+)-(?P<version>[^-]+)-(?P<build>\d+)")

def is_egg_name_valid(s):
    """
    Return True if the given string is a valid egg name (not including the
    .egg, e.g. 'Qt-4.8.5-2')
    """
    return _EGG_NAME_RE.match(s)

class Dependency(HasTraits):
    """
    Dependency model for entries in the package metadata inside EGG-INFO/spec/depend
    """
    name = Unicode()
    version_string = Unicode()
    build_number = Long(-1)

    @classmethod
    def from_string(cls, s):
        """
        Create a Dependency from string following a name-version-build format,
        e.g. 'Qt-4.8.5-2'.
        """
        m = _EGG_NAME_RE.match(s)
        if m is None:
            raise InvalidEggName(s)
        return cls(name=m.group('name'), version_string=m.group('version'),
                   build_number=int(m.group('build')))


    @classmethod
    def from_spec_string(cls, s):
        """
        Create a Dependency from a spec string (as used in EGG-INFO/spec/depend).
        """
        parts = s.split()
        if len(parts) == 1:
            name = parts[0]
            if "-" in name:
                raise InvalidDependencyString(name)
            return cls(name=name)
        elif len(parts) == 2:
            name, version = parts
            parts = version.split("-")
            if len(parts) == 2:
                upstream, build_number = parts
                build_number = int(build_number)
            else:
                upstream, build_number = version, -1
            return cls(name=name, version_string=upstream, build_number=build_number)
        else:
            raise InvalidDependencyString(name)

    def __str__(self):
        if len(self.version_string) > 0:
            if self.build_number > 0:
                return "{0} {1}-{2}".format(self.name, self.version_string, self.build_number)
            else:
                return "{0} {1}".format(self.name, self.version_string)
        else:
            return self.name
