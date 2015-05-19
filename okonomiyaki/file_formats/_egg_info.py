import posixpath
import re
import zipfile2

import six

from ..bundled.traitlets import (
    HasTraits, Enum, Instance, List, Long, Unicode
)
from ..errors import (
    InvalidDependencyString, InvalidEggName, InvalidMetadata
)
from ..platforms import Platform
from ..platforms.legacy import LegacyEPDPlatform
from ..utils import parse_assignments
from ..utils.traitlets import NoneOrInstance, NoneOrUnicode
from ..versions import EnpkgVersion
from ._package_info import PackageInfo


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
_SPEC_SUMMARY_LOCATION = posixpath.join(EGG_INFO_PREFIX, "spec", "summary")
_USR_PREFIX_LOCATION = posixpath.join(EGG_INFO_PREFIX, "usr")

# Kept for backward compatibility: python tag should be specified, we use this
# table for eggs that do not define the python tag.
_PYTHON_VERSION_TO_PYTHON_TAG = {
    "2.7": "cp27",
    "2.6": "cp26",
    "2.5": "cp25",
    "": None,
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


def split_egg_name(s):
    m = _EGG_NAME_RE.match(s)
    if m is None:
        raise InvalidEggName(s)
    else:
        name, version, build = m.groups()
        return name, version, int(build)


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


def _platform_from_raw_spec(raw_spec):
    """ Create a Platform instance from the metadata info returned by
    parse_rawspec.

    if no platform is defined ('platform' and 'osdist' set to None), then
    None is returned.
    """
    arch_string = raw_spec[_TAG_ARCH]
    platform_string = raw_spec[_TAG_PLATFORM]
    osdist_string = raw_spec[_TAG_OSDIST]
    if platform_string is None and osdist_string is None:
        return None
    else:
        return Platform.from_spec_depend_data(platform_string,
                                              osdist_string, arch_string)


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

    _epd_legacy_platform = NoneOrInstance(LegacyEPDPlatform)

    _metadata_version = Enum(["1.1", "1.2"], _METADATA_DEFAULT_VERSION)

    @classmethod
    def _from_data(cls, data):
        args = data.copy()
        args[_TAG_METADATA_VERSION] = args.get(_TAG_METADATA_VERSION,
                                               _METADATA_DEFAULT_VERSION)

        platform = _platform_from_raw_spec(args)
        for k in (_TAG_ARCH, _TAG_PLATFORM, _TAG_OSDIST):
            args.pop(k)

        if platform is None:
            _epd_legacy_platform = None
        else:
            _epd_legacy_platform = LegacyEPDPlatform(platform.epd_platform)
        args["_epd_legacy_platform"] = _epd_legacy_platform

        args[_TAG_PACKAGES] = [
            Dependency.from_spec_string(s) for s in args.get(_TAG_PACKAGES, [])
        ]

        return cls(**args)

    @classmethod
    def from_egg(cls, egg):
        with zipfile2.ZipFile(egg) as fp:
            try:
                spec_depend_string = fp.read(_SPEC_DEPEND_LOCATION).decode()
            except KeyError:
                msg = ("File {0!r} is not an Enthought egg (is missing {1})"
                       .format(egg, _SPEC_DEPEND_LOCATION))
                raise InvalidMetadata(msg)
            else:
                return cls.from_string(spec_depend_string)

    @classmethod
    def from_string(cls, spec_depend_string):
        return cls._from_data(_normalized_info_from_string(spec_depend_string))

    @property
    def arch(self):
        """
        Egg architecture.
        """
        if self._epd_legacy_platform is None:
            return None
        else:
            return self._epd_legacy_platform.arch

    @property
    def egg_name(self):
        """
        Full egg name (including .egg extension).
        """
        return egg_name(self.name, self.version, self.build)

    @property
    def osdist(self):
        if self._epd_legacy_platform is None:
            return None
        else:
            return self._epd_legacy_platform.osdist

    @property
    def platform(self):
        """
        The legacy platform name (sys.platform).
        """
        if self._epd_legacy_platform is None:
            return None
        else:
            return self._epd_legacy_platform.platform

    @property
    def metadata_version(self):
        return self._metadata_version

    @metadata_version.setter
    def metadata_version(self, value):
        self._metadata_version = value

    @property
    def metadata_version_info(self):
        return _metadata_version_to_tuple(self._metadata_version)

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


class Dependencies(object):
    def __init__(self, runtime=None, build=None):
        self.runtime = runtime or ()
        self.build = runtime or ()


_TAG_RE = re.compile("""
    (?P<interpreter>(cp|pp|cpython|py))
    (?P<version>([\d_]+))
""", flags=re.VERBOSE)


def _python_tag_to_python(python_tag):
    # This converts only python version we currently intent to support in
    # metadata version 1.x.
    if python_tag is None:
        return None

    generic_msg = "Python tag {0!r} not understood".format(python_tag)

    m = _TAG_RE.match(python_tag)
    if m is None:
        raise InvalidMetadata(generic_msg)
    else:
        d = m.groupdict()
        version = d["version"]
        if len(version) == 1:
            msg = "Version {0!r} not supported".format(version)
            raise InvalidMetadata(msg)
        elif len(version) == 2:
            return "{0}.{1}".format(version[0], version[1])
        else:
            raise InvalidMetadata(generic_msg)


def _metadata_version_to_tuple(metadata_version):
    """ Convert a metadata version string to a tuple for comparison."""
    return tuple(int(s) for s in metadata_version.split("."))


def _normalized_info_from_string(spec_depend_string):
    """ Return a 'normalized' dictionary from the given spec/depend string.

    Note: the name value is NOT lower-cased, so that the egg filename may
    rebuilt from the data.
    """
    raw_data = parse_rawspec(spec_depend_string)

    data = {}
    for k in (_TAG_METADATA_VERSION,
              _TAG_NAME, _TAG_VERSION, _TAG_BUILD,
              _TAG_ARCH, _TAG_OSDIST, _TAG_PLATFORM,
              _TAG_PYTHON, _TAG_PACKAGES):
        data[k] = raw_data[k]

    metadata_version_info = _metadata_version_to_tuple(
        data[_TAG_METADATA_VERSION]
    )
    if metadata_version_info[:2] < (1, 2):
        data[_TAG_PYTHON_TAG] = _get_default_python_tag(raw_data,
                                                        raw_data[_TAG_PYTHON])
    else:
        data[_TAG_PYTHON_TAG] = raw_data[_TAG_PYTHON_TAG]

    return data


class EggMetadata(object):
    """ Enthought egg metadata for format 1.x.
    """
    @classmethod
    def from_egg(cls, path_or_file):
        """ Create a EggMetadata instance from an existing Enthought egg.

        Parameters
        ----------
        path: str or file-like object.
            If a string, understood as the path to the egg. Otherwise,
            understood as a zipfile-like object.
        """
        def _read_summary(fp):
            summary_arcname = "EGG-INFO/spec/summary"
            try:
                summary = fp.read(summary_arcname)
            except KeyError:
                # the summary file may not exist for eggs built with
                # endist/repack
                summary = b""
            return summary.decode()

        if isinstance(path_or_file, six.string_types):
            spec_depend = LegacySpecDepend.from_egg(path_or_file)
            with zipfile2.ZipFile(path_or_file) as fp:
                summary = _read_summary(fp)
        else:
            spec_depend_string = (path_or_file.read(_SPEC_DEPEND_LOCATION)
                                  .decode())
            spec_depend = LegacySpecDepend.from_string(spec_depend_string)
            summary = _read_summary(path_or_file)

        pkg_info = PackageInfo.from_egg(path_or_file)

        return cls._from_spec_depend(spec_depend, pkg_info, summary)

    @classmethod
    def _from_spec_depend(cls, spec_depend, pkg_info, summary,
                          metadata_version_info=None):
        raw_name = spec_depend.name

        version = EnpkgVersion.from_upstream_and_build(spec_depend.version,
                                                       spec_depend.build)

        python_tag = spec_depend.python_tag

        if spec_depend._epd_legacy_platform is None:
            platform = None
        else:
            platform_string = str(spec_depend._epd_legacy_platform)
            platform = Platform.from_epd_platform_string(platform_string)

        dependencies = Dependencies(
            tuple(str(dep) for dep in spec_depend.packages)
        )

        metadata_version_info = (
            metadata_version_info or spec_depend.metadata_version_info
        )

        return cls(raw_name, version, platform, python_tag, dependencies,
                   pkg_info, summary, metadata_version_info)

    def __init__(self, raw_name, version, platform, python_tag, dependencies,
                 pkg_info, summary, metadata_version_info=None):
        """ EggMetadata instances encompass Enthought egg metadata.

        Parameters
        ----------
        raw_name: str
            The 'raw' name, i.e. the name value in spec/depend.
        version: EnpkgVersion
            The full version
        platform: Platform
            An okonomyaki platform instance, or None for cross-platform eggs
        python_tag: str
            The python tag, e.g. 'cp27'. May be None.
        dependencies: Dependencies
            A Dependencies instance.
        pkg_info: PackageInfo or None
            Instance modeling the PKG-INFO content of the egg.
        summary: str
            The summary. Models the string in EGG-INFO/spec/summary. May
            be empty.
        """
        self._raw_name = raw_name
        self.version = version

        self.platform = platform

        self._python = _python_tag_to_python(python_tag)
        self.python_tag = python_tag

        self.runtime_dependencies = tuple(dependencies.runtime)

        if metadata_version_info is None:
            self.metadata_version_info = _metadata_version_to_tuple(
                _METADATA_DEFAULT_VERSION
            )
        else:
            self.metadata_version_info = metadata_version_info

        self.pkg_info = pkg_info
        self.summary = summary

    @property
    def build(self):
        return self.version.build

    @property
    def egg_basename(self):
        return self._raw_name

    @property
    def egg_name(self):
        return self._spec_depend.egg_name

    @property
    def kind(self):
        return "egg"

    @property
    def name(self):
        return self._raw_name.lower().replace("-", "_")

    @property
    def spec_depend_string(self):
        return self._spec_depend.to_string()

    @property
    def upstream_version(self):
        return str(self.version.upstream)

    @property
    def _spec_depend(self):
        if self.platform is None:
            _epd_legacy_platform = None
        else:
            epd_platform = self.platform.epd_platform
            _epd_legacy_platform = LegacyEPDPlatform(epd_platform)

        args = {
            "name": self._raw_name,
            "version": self.upstream_version,
            "build": self.build,
            "python": self._python,
            "python_tag": self.python_tag,
            "packages": [
                Dependency.from_spec_string(dep)
                for dep in self.runtime_dependencies
            ],
            "_epd_legacy_platform": _epd_legacy_platform,
            "_metadata_version": ".".join(
                str(i) for i in self.metadata_version_info
            ),
        }
        return LegacySpecDepend(**args)
