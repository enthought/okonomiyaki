"""Traitlets-based models for egg-related metadata."""
from ..utils.traitlets import HasTraits, Long, Unicode

_EGG_PREFIX = "EGG-INFO"

class Dependency(HasTraits):
    """
    Dependency model for entries in the package metadata inside EGG-INFO/spec/depend
    """
    name = Unicode()
    version_string = Unicode()
    build_number = Long(-1)

    @classmethod
    def from_string(cls, s):
        parts = s.split()
        if len(parts) == 1:
            return cls(name=parts[0])
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
            raise ValueError("Unrecognized dependency format '{}'".format(s))

    def __str__(self):
        if len(self.version_string) > 0:
            if self.build_number > 0:
                return "{0} {1}-{2}".format(self.name, self.version_string, self.build_number)
            else:
                return "{0} {1}".format(self.name, self.version_string)
        else:
            return self.name
