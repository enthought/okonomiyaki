"""Traitlets-based models for egg-related metadata."""
import _ast
import ast
import json
import posixpath
import re

from ..bundled.traitlets import HasTraits, Instance, List, Long, Unicode
from ..errors import InvalidDependencyString, InvalidEggName, OkonomiyakiError
from ..platforms.legacy import LegacyEPDPlatform

_CAN_BE_NONE_KEYS = ("osdist", "platform", "python")

_EGG_NAME_RE = re.compile("""
    (?P<name>[\.\w]+)
    -
    (?P<version>[^-]+)
    -
    (?P<build>\d+)
    \.egg$""", re.VERBOSE)

_TRANSLATOR = {
    _ast.List: lambda v: v.elts,
    _ast.Num: lambda v: v.n,
    _ast.Str: lambda v: v.s
}

EGG_INFO_PREFIX = "EGG-INFO"

# Those may need to be public, depending on how well we can hide their
# locations or not.
_INFO_JSON_LOCATION = posixpath.join(EGG_INFO_PREFIX, "info.json")
_SPEC_DEPEND_LOCATION = posixpath.join(EGG_INFO_PREFIX, "spec", "depend")
_USR_PREFIX_LOCATION = posixpath.join(EGG_INFO_PREFIX, "usr")


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

def egg_name(name, version, build):
    """
    Return the egg filename (including the .egg extension) for the given
    arguments
    """
    return "{0}-{1}-{2}.egg".format(name, version, build)


def is_egg_name_valid(s):
    """
    Return True if the given string is a valid egg name (not including the
    .egg, e.g. 'Qt-4.8.5-2')
    """
    return _EGG_NAME_RE.match(s) is not None


def split_egg_name(s):
    m = _EGG_NAME_RE.match(s)
    if m is None:
        raise InvalidEggName(s)
    else:
        name, version, build = m.groups()
        return name, version, int(build)


def _decode_none_values(data, none_keys):
    for k in none_keys:
        if k in data and data[k] is None:
            data[k] = ""
    return data


def _encode_none_values(data, none_keys):
    # XXX: hack to deal with the lack of Either in traitlets -> ''
    # translated to null in json for those keys
    for k in none_keys:
        if k in data and data[k] == "":
            data[k] = None
    return data


# info_from_z and parse_rawspec are copied from egginst.eggmeta. Unlikely to
# change soon hopefully.
def info_from_z(z):
    """
    Create a 'spec-like' dictionary from an egg file object (i.e. a
    ZipFile instance).
    """
    res = {"type": "egg"}

    arcname = _SPEC_DEPEND_LOCATION
    if arcname in z.namelist():
        res.update(parse_rawspec(z.read(arcname).decode()))

    arcname = _INFO_JSON_LOCATION
    if arcname in z.namelist():
        res.update(json.loads(z.read(arcname)))

    res['name'] = res['name'].lower().replace('-', '_')
    return res


def parse_rawspec(spec_string):
    spec = _parse_assignments(spec_string.replace('\r', ''))
    res = {}
    for k in ('name', 'version', 'build',
              'arch', 'platform', 'osdist', 'python', 'packages'):
        res[k] = spec[k]
    return res


def _parse_assignments(s):
    """
    Parse a string of valid python code that consists only in a set of
    simple assignments.

    Parameters
    ----------
    s: str
        A string containing assignments only

    Example
    -------
    >>> _parse_assignments("foo = '1'\nbar = 2")
    {'foo': '1', 'bar': 2}
    """
    res = {}
    ast_result = ast.parse(s)

    for element in ast_result.body:
        if not isinstance(element, _ast.Assign):
            raise OkonomiyakiError("Invalid expression in string.")
        assignment = element
        if not len(assignment.targets) == 1:
            raise OkonomiyakiError("Invalid expression in string.")
        name = assignment.targets[0].id
        res[name] = _translator(assignment.value)
    return res


def _translator(v):
    if isinstance(v, _ast.Num) or isinstance(v, _ast.Str):
        return _TRANSLATOR[v.__class__](v)
    elif isinstance(v, _ast.List):
        return [_translator(i) for i in _TRANSLATOR[_ast.List](v)]
    elif isinstance(v, _ast.Name):
        if v.id != 'None':
            raise NotImplementedError("value of type _ast.Name which value "
                                      "!= 'None' not supported (was {0})".
                                      format(v.id))
        else:
            return None
    else:
        raise NotImplementedError("Type {0} not handled yet".format(v))
