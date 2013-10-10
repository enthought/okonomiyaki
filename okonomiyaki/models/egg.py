"""Traitlets-based models for egg-related metadata."""
from ..errors import InvalidDependencyString

from ..bundled.traitlets import HasTraits, Instance, List, Long, Unicode
from ..platform.legacy import LegacyEPDPlatform
from .common import (egg_name, _decode_none_values, _encode_none_values,
                     split_egg_name)

_CAN_BE_NONE_KEYS = ("osdist", "platform", "python")


class Dependency(HasTraits):
    """
    Dependency model for entries in the package metadata inside
    EGG-INFO/spec/depend
    """
    name = Unicode()
    version_string = Unicode()
    build_number = Long(-1)

    @property
    def strictness(self):
        if len(self.version_string) == 0:
            return 1
        elif self.build_number < 0:
            return 2
        else:
            return 3

    @classmethod
    def from_string(cls, s, strictness=2):
        """
        Create a Dependency from string following a name-version-build
        format.

        Parameters
        ----------
        s: str
            Egg name, e.g. 'Qt-4.8.5-2'.
        strictness: int
            Control strictness of string representation
        """
        name, version, build = split_egg_name("{0}.egg".format(s))
        if strictness >= 3:
            build_number = build
        else:
            build_number = -1

        if strictness >= 2:
            version_string = version
        else:
            version_string = ""

        return cls(name=name, version_string=version_string,
                   build_number=build_number)

    @classmethod
    def from_spec_string(cls, s):
        """
        Create a Dependency from a spec string (as used in
        EGG-INFO/spec/depend).
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
            return cls(name=name, version_string=upstream,
                       build_number=build_number)
        else:
            raise InvalidDependencyString(name)

    def __str__(self):
        if len(self.version_string) > 0:
            if self.build_number > 0:
                return "{0} {1}-{2}".format(self.name,
                                            self.version_string,
                                            self.build_number)
            else:
                return "{0} {1}".format(self.name, self.version_string)
        else:
            return self.name


class LegacySpec(HasTraits):
    """
    This models the EGG-INFO/spec content.
    """
    # Name is taken from egg path, so may be upper case
    name = Unicode()
    version = Unicode()
    build = Long()

    python = Unicode()
    packages = List(Instance(Dependency))

    lib_depend = List()
    lib_provide = List()

    summary = Unicode()

    _epd_legacy_platform = Instance(LegacyEPDPlatform)

    @property
    def arch(self):
        return self._epd_legacy_platform.arch

    @property
    def egg_name(self):
        return egg_name(self.name, self.version, self.build)

    @property
    def metadata_version(self):
        return "1.1"

    @property
    def osdist(self):
        return self._epd_legacy_platform.osdist

    @property
    def platform(self):
        return self._epd_legacy_platform.platform

    @property
    def short(self):
        return self._epd_legacy_platform.short

    @property
    def subdir(self):
        return self._epd_legacy_platform.subdir

    @classmethod
    def from_data(cls, data, epd_platform_string, python=None):
        args = data.copy()

        args["_epd_legacy_platform"] = \
            LegacyEPDPlatform.from_epd_platform_string(epd_platform_string)

        args["python"] = python

        args = _decode_none_values(args, _CAN_BE_NONE_KEYS)
        return cls(**args)

    @classmethod
    def from_egg(cls, egg, epd_platform, python=None):
        name, version, build = split_egg_name(egg)
        data = dict(name=name, version=version, build=build)
        return cls.from_data(data, epd_platform, python)

    def to_dict(self):
        data = {"name": self.name,
                "version": self.version,
                "build": self.build,
                "arch": self.arch,
                "platform": self.platform,
                "osdist": self.osdist,
                "packages": [str(p) for p in self.packages],
                "python": self.python,
                "short": self.short,
                "subdir": self.subdir,
                "metadata_version": self.metadata_version}
        data = _encode_none_values(data, _CAN_BE_NONE_KEYS)

        if len(self.lib_depend) > 0:
            data["lib-depend"] = "\n".join(str(p) for p in self.lib_depend)
        else:
            data["lib-depend"] = "\n"
        if len(self.lib_provide):
            data["lib-provide"] = "\n".join(str(p) for p in self.lib_provide)
        else:
            data["lib-provide"] = "\n"

        return data

    def depend_content(self):
        """
        Returns a string that is suitable for the depend file inside our
        legacy egg.
        """
        template = """\
metadata_version = '{metadata_version}'
name = '{name}'
version = '{version}'
build = {build}

arch = '{arch}'
platform = '{platform}'
osdist = '{osdist}'
python = '{python}'
packages = {packages}
"""
        data = self.to_dict()

        # This is just to ensure the exact same string as the produced by the
        # legacy buildsystem
        if len(self.packages) == 0:
            data["packages"] = "[]"
        else:
            data["packages"] = "[\n  {0},\n]". \
                format("  \n".join("'{0}'".format(p)
                       for p in self.packages))
        return template.format(**data)
