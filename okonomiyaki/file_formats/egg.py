import json
import os
import re
import posixpath
import zipfile

import os.path as op

import six

from ..bundled.traitlets import (HasTraits, Bool, Enum, Instance, List, Long,
                                 Unicode)
from ..errors import InvalidDependencyString, InvalidEggName, InvalidMetadata
from ..platforms.legacy import LegacyEPDPlatform
from ..utils import parse_assignments
from ..utils.traitlets import NoneOrUnicode

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

# Kept for backward compatibility: python tag should be specified, we use this
# table for eggs that do not define the python tag.
_PYTHON_VERSION_TO_PYTHON_TAG = {
    "2.7": "cp27",
    "2.6": "cp26",
    "2.5": "cp25",
    None: None,
}

_TAG_METADATA_VERSION = "metadata_version"
_TAG_NAME = "name"
_TAG_VERSION = "version"
_TAG_BUILD = "build"
_TAG_ARCH = "arch"
_TAG_OSDIST = "osdist"
_TAG_PLATFORM = "platform"
_TAG_PYTHON = "python"
_TAG_PYTHON_TAG = "python_tag"
_TAG_PACKAGES = "packages"

_METADATA_VERSION_TO_KEYS = {
    "1.1": (_TAG_METADATA_VERSION, _TAG_NAME, _TAG_VERSION, _TAG_BUILD,
            _TAG_ARCH, _TAG_PLATFORM, _TAG_OSDIST, _TAG_PYTHON, _TAG_PACKAGES),
}
_METADATA_VERSION_TO_KEYS["1.2"] = \
    _METADATA_VERSION_TO_KEYS["1.1"] + (_TAG_PYTHON_TAG, )

_UNSUPPORTED = "unsupported"


class Dependency(HasTraits):
    """
    Dependency model for entries in the package metadata inside
    EGG-INFO/spec/depend
    """
    name = Unicode()
    version_string = Unicode()
    build_number = Long(-1)

    def __init__(self, name="", version_string="", build_number=-1):
        self.name = name
        self.version_string = version_string
        self.build_number = build_number
        super(Dependency, self).__init__(self, name, version_string,
                                         build_number)

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


_METADATA_TEMPLATES = {
    "1.1": """\
metadata_version = '1.1'
name = {name!r}
version = {version!r}
build = {build}

arch = {arch!r}
platform = {platform!r}
osdist = {osdist!r}
python = {python!r}
packages = {packages}
""",
    "1.2": """\
metadata_version = '1.2'
name = {name!r}
version = {version!r}
build = {build}

arch = {arch!r}
platform = {platform!r}
osdist = {osdist!r}
python = {python!r}
python_tag = {python_tag!r}
packages = {packages}
"""
}


def _get_default_python_tag(data, python):
    python_tag = data.get(_TAG_PYTHON_TAG)
    if python_tag is None:
        python_tag = _PYTHON_VERSION_TO_PYTHON_TAG.get(python, _UNSUPPORTED)
        if python_tag == _UNSUPPORTED:
            msg = "python = {0} is not supported for metadata_version " \
                  "= {1!r}".format(python, data[_TAG_METADATA_VERSION])
            raise InvalidMetadata(msg, _TAG_PYTHON_TAG)

    return python_tag


_METADATA_DEFAULT_VERSION = "1.2"


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

    python = NoneOrUnicode()
    """
    Python version
    """
    python_tag = NoneOrUnicode()
    """
    Python tag (as defined in PEP 425)
    """

    packages = List(Instance(Dependency))
    """
    List of dependencies for this egg
    """

    _epd_legacy_platform = Instance(LegacyEPDPlatform)

    _metadata_version = Enum(["1.1", "1.2"], _METADATA_DEFAULT_VERSION)

    @classmethod
    def from_data(cls, data, epd_platform_string, python=None,
                  python_tag=None):
        args = data.copy()
        args[_TAG_METADATA_VERSION] = args.get(_TAG_METADATA_VERSION,
                                               _METADATA_DEFAULT_VERSION)

        args["_epd_legacy_platform"] = \
            LegacyEPDPlatform.from_epd_platform_string(epd_platform_string)

        args[_TAG_PYTHON] = python
        args[_TAG_PYTHON_TAG] = python_tag or _get_default_python_tag(args,
                                                                      python)

        args[_TAG_PACKAGES] = [
            Dependency.from_spec_string(s) for s in args.get(_TAG_PACKAGES, [])
        ]

        return cls(**args)

    @classmethod
    def from_egg(cls, egg, epd_platform):
        name, version, build = split_egg_name(op.basename(egg))
        data = dict(name=name, version=version, build=build)

        fp = zipfile.ZipFile(egg)
        try:
            info_data = info_from_z(fp)
            if _TAG_PYTHON in info_data:
                python = info_data[_TAG_PYTHON]
            else:
                python = None

            python_tag = _get_default_python_tag(data, python)

            data[_TAG_PACKAGES] = info_data[_TAG_PACKAGES]
            if _TAG_METADATA_VERSION in info_data:
                data[_TAG_METADATA_VERSION] = info_data[_TAG_METADATA_VERSION]
        finally:
            fp.close()
        return cls.from_data(data, epd_platform, python, python_tag)

    @classmethod
    def from_string(cls, spec_depend_string, epd_platform_string=None):
        raw_data = parse_rawspec(spec_depend_string)

        data = {
            _TAG_NAME: raw_data[_TAG_NAME],
            _TAG_VERSION: raw_data[_TAG_VERSION],
            _TAG_BUILD: raw_data[_TAG_BUILD],
            _TAG_PACKAGES: raw_data[_TAG_PACKAGES],
        }

        data[_TAG_METADATA_VERSION] = raw_data[_TAG_METADATA_VERSION]

        python = raw_data[_TAG_PYTHON]
        python_tag = _get_default_python_tag(raw_data, python)

        arch, osdist = raw_data[_TAG_ARCH], raw_data[_TAG_OSDIST]
        if epd_platform_string is not None:
            epd_platform = \
                LegacyEPDPlatform.from_epd_platform_string(epd_platform_string)
            if arch is not None:
                if not arch == epd_platform.arch:
                    msg = "Arch mismatch: {0!r} found in spec/depend, but " \
                          "{1!r} specified".format(arch, epd_platform.arch)
                    raise InvalidMetadata(msg, _TAG_ARCH)
            if osdist is not None:
                if not osdist == epd_platform.osdist:
                    msg = "Osdist mismatch: {0!r} found in spec/depend, but " \
                          "{1!r} specified".format(osdist, epd_platform.osdist)
                    raise InvalidMetadata(_TAG_OSDIST, msg)
        else:
            if osdist is None:
                msg = "Cannot guess platform for egg with osdist = None"
                raise InvalidMetadata(msg, _TAG_OSDIST)

            epd_platform = \
                LegacyEPDPlatform.from_arch_and_osdist(arch, osdist)
        return cls.from_data(data, epd_platform.short, python, python_tag)

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
        return self._metadata_version

    @metadata_version.setter
    def metadata_version(self, value):
        self._metadata_version = value

    def _to_dict(self):
        raw_data = {
            _TAG_NAME: self.name,
            _TAG_VERSION: self.version,
            _TAG_BUILD: self.build,
            _TAG_ARCH: self.arch,
            _TAG_PLATFORM: self.platform,
            _TAG_OSDIST: self.osdist,
            _TAG_PACKAGES: [str(p) for p in self.packages],
            _TAG_PYTHON: self.python,
            _TAG_PYTHON_TAG: self.python_tag,
            _TAG_METADATA_VERSION: self.metadata_version
        }

        ret = {}
        for k, v in raw_data.items():
            if isinstance(v, six.string_types):
                v = str(v)
            ret[k] = v
        return ret

    def to_string(self):
        """
        Returns a string that is suitable for the depend file inside our
        legacy egg.
        """
        template = _METADATA_TEMPLATES.get(self.metadata_version, None)
        data = self._to_dict()

        # This is just to ensure the exact same string as the produced by the
        # legacy buildsystem
        if len(self.packages) == 0:
            data[_TAG_PACKAGES] = "[]"
        else:
            data[_TAG_PACKAGES] = "[\n{0}\n]". \
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

    metadata_version = spec.get(_TAG_METADATA_VERSION)
    if metadata_version is None \
            or metadata_version not in _METADATA_VERSION_TO_KEYS:
        msg = "Invalid metadata version: {0!r}".format(metadata_version)
        raise InvalidMetadata(msg, _TAG_METADATA_VERSION)

    res = {}

    keys = _METADATA_VERSION_TO_KEYS.get(metadata_version)
    for key in keys:
        try:
            res[key] = spec[key]
        except KeyError:
            msg = "Missing attribute {0!r} (metadata_version: {1!r})"
            raise InvalidMetadata(msg.format(key, metadata_version), key)
    return res
