import json
import os
import re
import posixpath
import zipfile

import os.path as op

import six

from ..bundled.traitlets import HasTraits, Bool, Instance, List, Long, Unicode
from ..errors import InvalidDependencyString, InvalidEggName
from ..platforms.legacy import LegacyEPDPlatform
from ..utils import parse_assignments

_CAN_BE_NONE_KEYS = ("osdist", "platform", "python")

_EGG_NAME_RE = re.compile("""
    (?P<name>[\.\w]+)
    -
    (?P<version>[^-]+)
    -
    (?P<build>\d+)
    \.egg$""", re.VERBOSE)

EGG_INFO_PREFIX = "EGG-INFO"

# Those may need to be public, depending on how well we can hide their
# locations or not.
_INFO_JSON_LOCATION = posixpath.join(EGG_INFO_PREFIX, "info.json")
_SPEC_DEPEND_LOCATION = posixpath.join(EGG_INFO_PREFIX, "spec", "depend")
_SPEC_LIB_DEPEND_LOCATION = posixpath.join(EGG_INFO_PREFIX, "spec",
                                           "lib-depend")
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


class LegacySpecDepend(HasTraits):
    """
    This models the EGG-INFO/spec/depend content.
    """
    # Name is taken from egg path, so may be upper case
    name = Unicode()
    """
    Egg name
    """
    version = Unicode()
    """
    Upstream version (as a string).
    """
    build = Long()
    """
    Build number
    """

    python = Unicode()
    """
    Python version
    """
    packages = List(Instance(Dependency))
    """
    List of dependencies for this egg
    """

    _epd_legacy_platform = Instance(LegacyEPDPlatform)

    @classmethod
    def from_data(cls, data, epd_platform_string, python=None):
        args = data.copy()

        args["_epd_legacy_platform"] = \
            LegacyEPDPlatform.from_epd_platform_string(epd_platform_string)

        args["python"] = python

        args["packages"] = [
            Dependency.from_spec_string(s) for s in args.get("packages", [])
        ]

        args = _decode_none_values(args, _CAN_BE_NONE_KEYS)
        return cls(**args)

    @classmethod
    def from_egg(cls, egg, epd_platform):
        name, version, build = split_egg_name(op.basename(egg))
        data = dict(name=name, version=version, build=build)

        fp = zipfile.ZipFile(egg)
        try:
            info_data = info_from_z(fp)
            if "python" in info_data:
                python = info_data["python"]
            else:
                python = None

            data["packages"] = info_data["packages"]
        finally:
            fp.close()
        return cls.from_data(data, epd_platform, python)

    @classmethod
    def from_string(cls, spec_depend_string):
        raw_data = parse_rawspec(spec_depend_string)

        data = {
            "name": raw_data["name"],
            "version": raw_data["version"],
            "build": raw_data["build"],
            "packages": raw_data["packages"],
        }

        python = raw_data["python"]

        arch, osdist = raw_data["arch"], raw_data["osdist"]
        epd_platform = LegacyEPDPlatform.from_arch_and_osdist(arch,
                                                              osdist)
        return cls.from_data(data, epd_platform.short, python)

    @property
    def arch(self):
        """
        Egg architecture.
        """
        return self._epd_legacy_platform.arch

    @property
    def egg_name(self):
        """
        Full egg name (including .egg extension).
        """
        return egg_name(self.name, self.version, self.build)

    @property
    def osdist(self):
        return self._epd_legacy_platform.osdist

    @property
    def platform(self):
        """
        The legacy platform name (sys.platform).
        """
        return self._epd_legacy_platform.platform

    @property
    def metadata_version(self):
        return "1.1"

    def _to_dict(self):
        data = {"name": self.name,
                "version": self.version,
                "build": self.build,
                "arch": self.arch,
                "platform": self.platform,
                "osdist": self.osdist,
                "packages": [str(p) for p in self.packages],
                "python": self.python,
                "metadata_version": self.metadata_version}
        return _encode_none_values(data, _CAN_BE_NONE_KEYS)

    def to_string(self):
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
        data = self._to_dict()

        # This is just to ensure the exact same string as the produced by the
        # legacy buildsystem
        if len(self.packages) == 0:
            data["packages"] = "[]"
        else:
            data["packages"] = "[\n{0}\n]". \
                format("\n".join("  '{0}',".format(p)
                       for p in self.packages))
        return template.format(**data)


class LegacySpec(HasTraits):
    """
    This models the EGG-INFO/spec content.
    """
    depend = Instance(LegacySpecDepend)
    """
    Models the spec/depend content
    """

    lib_depend = List()
    """
    List of freeform content
    """
    lib_provide = List()
    """
    List of freeform content
    """

    summary = Unicode()
    """
    Summary metadata of the egg.
    """

    @classmethod
    def from_egg(cls, egg, epd_platform):
        spec_depend = LegacySpecDepend.from_egg(egg, epd_platform)

        data = {"depend": spec_depend}

        fp = zipfile.ZipFile(egg)
        try:
            try:
                lib_depend_data = fp.read(_SPEC_LIB_DEPEND_LOCATION).decode()
                data["lib_depend"] = lib_depend_data.splitlines()
            except KeyError:
                pass
        finally:
            fp.close()

        return cls(**data)

    @property
    def egg_name(self):
        return "{0}-{1}-{2}.egg".format(self.depend.name,
                                        self.depend.version,
                                        self.depend.build)

    def depend_content(self):
        return self.depend.to_string()

    def lib_depend_content(self):
        """
        Returns a string that is suitable for the lib-depend file inside our
        legacy egg.
        """
        # The added "" is for round-tripping with the current egg format
        return "\n".join(str(entry) for entry in self.lib_depend + [""])


class EggBuilder(HasTraits):
    """
    Class to build eggs from an install tree.
    """
    compress = Bool()
    """
    True if the egg must be compressed.
    """
    cwd = Unicode()
    """
    Root directory from which paths will be resolved.
    """
    spec = Instance(LegacySpec)
    """
    Spec instance
    """

    _fp = Instance(zipfile.ZipFile)

    def __init__(self, spec, cwd=None, compress=True):
        if cwd is None:
            cwd = os.getcwd()

        super(EggBuilder, self).__init__(spec=spec, cwd=cwd, compres=compress)

        if compress is True:
            self._fp = zipfile.ZipFile(self.egg_path, "w",
                                       zipfile.ZIP_DEFLATED)
        else:
            self._fp = zipfile.ZipFile(self.egg_path, "w")

    @property
    def egg_path(self):
        return op.join(self.cwd, self.spec.egg_name)

    def close(self):
        self._write_spec_depend()
        self._fp.close()

    def __enter__(self):
        return self

    def __exit__(self, *a, **kw):
        self.close()

    def add_usr_files_iterator(self, it):
        """
        Add the given files to the egg inside the usr subdirectory (i.e. not
        in site-packages).

        Parameters
        ----------
        it: generator
            Assumed to yield pairs (path, arcname) where path is the path of
            the file to write into the archive, and arcname the archive name
            relative to the usr subdirectory, i.e. ('foo.h', 'include/foo.h')
            will write foo.h as EGG-INFO/usr/include/foo.h).
        """
        for path, arcname in it:
            self._fp.write(path, posixpath.join(_USR_PREFIX_LOCATION, arcname))

    def _write_spec_depend(self):
        self._fp.writestr(_SPEC_DEPEND_LOCATION, self.spec.depend_content())


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
        res.update(json.loads(z.read(arcname).decode()))

    res['name'] = res['name'].lower().replace('-', '_')
    return res


def parse_rawspec(spec_string):
    spec = parse_assignments(six.StringIO(spec_string.replace('\r', '')))
    res = {}
    for k in ('name', 'version', 'build',
              'arch', 'platform', 'osdist', 'python', 'packages'):
        res[k] = spec[k]
    return res
