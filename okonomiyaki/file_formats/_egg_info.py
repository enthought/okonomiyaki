import posixpath
import re
import zipfile2

from ..bundled.traitlets import (
    HasTraits, Enum, Instance, List, Long, Unicode
)
from ..errors import (
    InvalidRequirementString, InvalidEggName, InvalidMetadata,
    UnsupportedMetadata
)
from ..platforms import EPDPlatform
from ..platforms.legacy import LegacyEPDPlatform
from ..utils import compute_sha256, parse_assignments
from ..utils.py3compat import StringIO, string_types
from ..utils.traitlets import NoneOrInstance, NoneOrUnicode
from ..versions import EnpkgVersion
from .pep425 import PythonImplementation
from ._blacklist import (
    EGG_PLATFORM_BLACK_LIST, EGG_PYTHON_TAG_BLACK_LIST,
    may_be_in_platform_blacklist, may_be_in_python_tag_blacklist
)
from ._package_info import PackageInfo, _keep_position, _read_pkg_info


_EGG_NAME_RE = re.compile("""
    (?P<name>[\.\w]+)
    -
    (?P<version>[^-]+)
    -
    (?P<build>\d+)
    \.egg$""", re.VERBOSE)

_PYVER_RE = re.compile("(?P<major>\d+)\.(?P<minor>\d+)")

EGG_INFO_PREFIX = "EGG-INFO"

# Those may need to be public, depending on how well we can hide their
# locations or not.
_INFO_JSON_LOCATION = posixpath.join(EGG_INFO_PREFIX, "info.json")
_SPEC_DEPEND_LOCATION = posixpath.join(EGG_INFO_PREFIX, "spec", "depend")
_SPEC_LIB_DEPEND_LOCATION = posixpath.join(EGG_INFO_PREFIX, "spec",
                                           "lib-depend")
_SPEC_SUMMARY_LOCATION = posixpath.join(EGG_INFO_PREFIX, "spec", "summary")
_USR_PREFIX_LOCATION = posixpath.join(EGG_INFO_PREFIX, "usr")

_TAG_METADATA_VERSION = "metadata_version"
_TAG_NAME = "name"
_TAG_VERSION = "version"
_TAG_BUILD = "build"
_TAG_ARCH = "arch"
_TAG_OSDIST = "osdist"
_TAG_PLATFORM = "platform"
_TAG_PYTHON = "python"
_TAG_PYTHON_PEP425_TAG = "python_tag"
_TAG_ABI_PEP425_TAG = "abi_tag"
_TAG_PLATFORM_PEP425_TAG = "platform_tag"
_TAG_PACKAGES = "packages"

_METADATA_VERSION_TO_KEYS = {
    "1.1": (_TAG_METADATA_VERSION, _TAG_NAME, _TAG_VERSION, _TAG_BUILD,
            _TAG_ARCH, _TAG_PLATFORM, _TAG_OSDIST, _TAG_PYTHON, _TAG_PACKAGES),
}
_METADATA_VERSION_TO_KEYS["1.2"] = \
    _METADATA_VERSION_TO_KEYS["1.1"] + (_TAG_PYTHON_PEP425_TAG, )

_METADATA_VERSION_TO_KEYS["1.3"] = (
    _METADATA_VERSION_TO_KEYS["1.2"] +
    (_TAG_ABI_PEP425_TAG, _TAG_PLATFORM_PEP425_TAG)
)

_UNSUPPORTED = "unsupported"

_PYVER_RE = re.compile("(?P<major>\d).(?P<minor>\d)")


def split_egg_name(s):
    m = _EGG_NAME_RE.match(s)
    if m is None:
        raise InvalidEggName(s)
    else:
        name, version, build = m.groups()
        return name, version, int(build)


def parse_rawspec(spec_string):
    spec = parse_assignments(StringIO(spec_string.replace('\r', '')))

    metadata_version = spec.get(_TAG_METADATA_VERSION)
    if metadata_version is None \
            or metadata_version not in _METADATA_VERSION_TO_KEYS:
        msg = ("Invalid metadata version: {0!r}. You may need to update to a "
               "more recent okonomiyaki version".format(metadata_version))
        raise UnsupportedMetadata(msg)

    res = {}

    keys = _METADATA_VERSION_TO_KEYS.get(metadata_version)
    for key in keys:
        try:
            res[key] = spec[key]
        except KeyError:
            msg = "Missing attribute {0!r} (metadata_version: {1!r})"
            raise InvalidMetadata(msg.format(key, metadata_version))
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


_INVALID_REQUIREMENTS = {
    "numpy-1.8.0": "numpy 1.8.0",
}


def _translate_invalid_requirement(s):
    return _INVALID_REQUIREMENTS.get(s, s)


class Requirement(HasTraits):
    """
    Model for entries in the package metadata inside EGG-INFO/spec/depend
    """
    name = Unicode()
    version_string = Unicode()
    build_number = Long(-1)

    def __init__(self, name="", version_string="", build_number=-1):
        self.name = name
        self.version_string = version_string
        self.build_number = build_number
        super(Requirement, self).__init__(self, name, version_string,
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
        Create a Requirement from string following a name-version-build
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
        Create a Requirement from a spec string (as used in
        EGG-INFO/spec/depend).
        """
        s = _translate_invalid_requirement(s)
        parts = s.split()
        if len(parts) == 1:
            name = parts[0]
            if "-" in name:
                raise InvalidRequirementString(name)
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
            raise InvalidRequirementString(name)

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

    @property
    def _key(self):
        return (self.name, self.version_string, self.build_number)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self._key == other._key

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self._key)


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
""",
    "1.3": """\
metadata_version = '1.3'
name = {name!r}
version = {version!r}
build = {build}

arch = {arch!r}
platform = {platform!r}
osdist = {osdist!r}
python = {python!r}

python_tag = {python_tag!r}
abi_tag = {abi_tag!r}
platform_tag = {platform_tag!r}

packages = {packages}
"""
}


def _guess_python_tag(pyver):
    """ Guess python_tag from the given python string ("MAJOR.MINOR", e.g. "2.7").

    None may be returned (for egg that don't depend on python)
    """
    if pyver in (None, ""):
        return None
    else:
        m = _PYVER_RE.search(pyver)
        if m is None:
            msg = "python_tag cannot be guessed for python = {0}"
            raise InvalidMetadata(msg.format(pyver))
        else:
            major = m.groupdict()["major"]
            minor = m.groupdict()["minor"]

            return "cp" + major + minor


_METADATA_DEFAULT_VERSION = "1.3"


def _epd_platform_from_raw_spec(raw_spec):
    """ Create an EPDPlatform instance from the metadata info returned by
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
        return EPDPlatform._from_spec_depend_data(
            platform_string, osdist_string, arch_string
        )


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
    Python tag (as defined in PEP 425).
    """

    abi_tag = NoneOrUnicode()
    """
    ABI tag (as defined in PEP 425), except that 'none' is None.
    """

    platform_tag = NoneOrUnicode()
    """
    Platform tag (as defined in PEP 425), except that 'any' is None.
    """

    packages = List(Instance(Requirement))
    """
    List of dependencies for this egg
    """

    _epd_legacy_platform = NoneOrInstance(LegacyEPDPlatform)

    _metadata_version = Enum(["1.1", "1.2", "1.3"], _METADATA_DEFAULT_VERSION)

    @classmethod
    def _from_data(cls, data, epd_platform):
        args = data.copy()
        args[_TAG_METADATA_VERSION] = args.get(_TAG_METADATA_VERSION,
                                               _METADATA_DEFAULT_VERSION)

        if epd_platform is None:
            _epd_legacy_platform = None
        else:
            _epd_legacy_platform = LegacyEPDPlatform(epd_platform)
        args["_epd_legacy_platform"] = _epd_legacy_platform

        args[_TAG_PACKAGES] = [
            Requirement.from_spec_string(s)
            for s in args.get(_TAG_PACKAGES, [])
        ]

        return cls(**args)

    @classmethod
    def from_egg(cls, path_or_file):
        sha256 = None
        if isinstance(path_or_file, string_types):
            if (
                may_be_in_platform_blacklist(path_or_file)
                or may_be_in_python_tag_blacklist(path_or_file)
            ):
                sha256 = compute_sha256(path_or_file)
        else:
            with _keep_position(path_or_file.fp):
                sha256 = compute_sha256(path_or_file.fp)
        return cls._from_egg(path_or_file, sha256)

    @classmethod
    def _from_egg(cls, path_or_file, sha256):
        def _create_spec_depend(zp):
            epd_platform_string = EGG_PLATFORM_BLACK_LIST.get(sha256)
            if epd_platform_string is None:
                epd_platform = None
            else:
                epd_platform = EPDPlatform.from_epd_string(epd_platform_string)

            try:
                spec_depend_string = zp.read(_SPEC_DEPEND_LOCATION).decode()
            except KeyError:
                msg = ("File {0!r} is not an Enthought egg (is missing {1})"
                       .format(path_or_file, _SPEC_DEPEND_LOCATION))
                raise InvalidMetadata(msg)
            else:
                data, epd_platform = _normalized_info_from_string(
                    spec_depend_string, epd_platform,
                )
                python_tag = EGG_PYTHON_TAG_BLACK_LIST.get(sha256)
                if python_tag:
                    data[_TAG_PYTHON_PEP425_TAG] = python_tag
                return cls._from_data(data, epd_platform)

        if isinstance(path_or_file, string_types):
            with zipfile2.ZipFile(path_or_file) as zp:
                return _create_spec_depend(zp)
        else:
            return _create_spec_depend(path_or_file)

    @classmethod
    def from_string(cls, spec_depend_string):
        data, epd_platform = _normalized_info_from_string(spec_depend_string)
        return cls._from_data(data, epd_platform)

    @property
    def arch(self):
        """
        Egg architecture.
        """
        if self._epd_legacy_platform is None:
            return None
        else:
            return self._epd_legacy_platform.arch._legacy_name

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
            _TAG_PYTHON_PEP425_TAG: self.python_tag,
            _TAG_ABI_PEP425_TAG: self.abi_tag,
            _TAG_PLATFORM_PEP425_TAG: self.platform_tag,
            _TAG_METADATA_VERSION: self.metadata_version
        }

        ret = {}
        for k, v in raw_data.items():
            if isinstance(v, string_types):
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
    """ Object storing the various dependencies for an egg.

    Each attribute is a tuple of Requirement instances.
    """
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
            if version == "2":
                return "2.7"
            else:
                raise InvalidMetadata(generic_msg)
        elif len(version) == 2:
            return "{0}.{1}".format(version[0], version[1])
        else:
            raise InvalidMetadata(generic_msg)


def _metadata_version_to_tuple(metadata_version):
    """ Convert a metadata version string to a tuple for comparison."""
    return tuple(int(s) for s in metadata_version.split("."))


def _guess_abi_tag(platform, python_tag):
    assert python_tag is not None, "BUG, this function expects a python_tag"

    # For legacy (aka legacy spec version info < 1.3), we know that pyver
    # can only be one of "2.X" with X in (5, 6, 7).
    #
    # In those cases, the mapping (platform pyver) -> ABI is unambiguous,
    # as we only ever used one ABI for a given python version/platform.
    pyver = _python_tag_to_python(python_tag)
    return "cp{0}{1}m".format(pyver[0], pyver[2])


def _guess_platform_tag(platform):
    if platform is None:
        return None

    return platform.pep425_tag


def _normalized_info_from_string(spec_depend_string, epd_platform=None):
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

    epd_platform = epd_platform or _epd_platform_from_raw_spec(data)
    for k in (_TAG_ARCH, _TAG_PLATFORM, _TAG_OSDIST):
        data.pop(k)

    metadata_version_info = _metadata_version_to_tuple(
        data[_TAG_METADATA_VERSION]
    )
    if metadata_version_info[:2] < (1, 2):
        data[_TAG_PYTHON_PEP425_TAG] = _guess_python_tag(raw_data[_TAG_PYTHON])
    else:
        data[_TAG_PYTHON_PEP425_TAG] = raw_data[_TAG_PYTHON_PEP425_TAG]

    if metadata_version_info[:2] < (1, 3):
        python_tag = data[_TAG_PYTHON_PEP425_TAG]

        if python_tag is None:
            # No python tag, so should only be a "pure binary" egg, i.e.
            # an egg containing no python code and no python C extensions.
            abi = None
        elif epd_platform is None:
            # No platform, so should only be a "pure python" egg, i.e.
            # an egg containing no C extension.
            abi = None
        else:
            abi = _guess_abi_tag(epd_platform, python_tag)
        data[_TAG_ABI_PEP425_TAG] = abi
    else:
        data[_TAG_ABI_PEP425_TAG] = raw_data[_TAG_ABI_PEP425_TAG]

    if metadata_version_info[:2] < (1, 3):
        if epd_platform is None:
            platform_tag = None
        else:
            platform_tag = _guess_platform_tag(epd_platform)
        data[_TAG_PLATFORM_PEP425_TAG] = platform_tag
    else:
        data[_TAG_PLATFORM_PEP425_TAG] = raw_data[_TAG_PLATFORM_PEP425_TAG]

    return data, epd_platform


class EggMetadata(object):
    """ Enthought egg metadata for format 1.x.
    """
    @classmethod
    def from_egg(cls, path_or_file, strict=True):
        """ Create a EggMetadata instance from an existing Enthought egg.

        Parameters
        ----------
        path: str or file-like object.
            If a string, understood as the path to the egg. Otherwise,
            understood as a zipfile-like object.
        strict: bool
            If True, will fail if metadata cannot be decoded correctly (e.g.
            unicode errors in EGG-INFO/PKG-INFO). If false, will ignore those
            errors, at the risk of data loss.
        """
        sha256 = None
        if isinstance(path_or_file, string_types):
            if (
                may_be_in_platform_blacklist(path_or_file)
                or may_be_in_python_tag_blacklist(path_or_file)
            ):
                sha256 = compute_sha256(path_or_file)
        else:
            with _keep_position(path_or_file.fp):
                sha256 = compute_sha256(path_or_file.fp)
        return cls._from_egg(path_or_file, sha256, strict)

    @classmethod
    def _from_egg(cls, path_or_file, sha256, strict=True):
        def _read_summary(fp):
            summary_arcname = "EGG-INFO/spec/summary"
            try:
                summary = fp.read(summary_arcname)
            except KeyError:
                # the summary file may not exist for eggs built with
                # endist/repack
                summary = b""
            return summary.decode("utf8")

        spec_depend = LegacySpecDepend._from_egg(path_or_file, sha256)

        if isinstance(path_or_file, string_types):
            with zipfile2.ZipFile(path_or_file) as fp:
                summary = _read_summary(fp)
                pkg_info_data = _read_pkg_info(fp)
        else:
            summary = _read_summary(path_or_file)
            pkg_info_data = _read_pkg_info(path_or_file)

        if pkg_info_data is None:
            pkg_info = None
        else:
            pkg_info = PackageInfo._from_egg(path_or_file, sha256, strict)

        return cls._from_spec_depend(spec_depend, pkg_info, summary)

    @classmethod
    def _from_spec_depend(cls, spec_depend, pkg_info, summary,
                          metadata_version_info=None):
        raw_name = spec_depend.name

        version = EnpkgVersion.from_upstream_and_build(spec_depend.version,
                                                       spec_depend.build)

        python_tag = spec_depend.python_tag
        abi_tag = spec_depend.abi_tag

        if spec_depend._epd_legacy_platform is None:
            platform = None
        else:
            platform_string = str(spec_depend._epd_legacy_platform)
            platform = EPDPlatform.from_epd_string(platform_string)

        dependencies = Dependencies(
            tuple(dep for dep in spec_depend.packages)
        )

        metadata_version_info = (
            metadata_version_info or spec_depend.metadata_version_info
        )

        return cls(raw_name, version, platform, python_tag, abi_tag,
                   dependencies, pkg_info, summary, metadata_version_info)

    def __init__(self, raw_name, version, platform, python, abi_tag,
                 dependencies, pkg_info, summary, metadata_version_info=None):
        """ EggMetadata instances encompass Enthought egg metadata.

        Note: the constructor is considered private, please use one of the
        from_* class methods.

        Parameters
        ----------
        raw_name: str
            The 'raw' name, i.e. the name value in spec/depend.
        version: EnpkgVersion
            The full version
        platform: EPDPlatform
            An EPDPlatform instance, or None for cross-platform eggs
        python: Python
            The python implementation
        abi_tag: str
            The ABI tag, e.g. 'cp27m'. May be None.
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
        """ The version, as an EnpkgVersion instance."""

        self.platform = platform
        """ The platform, as a Platform instance."""

        if isinstance(python, string_types):
            python = PythonImplementation.from_string(python)
        self.python = python
        """ The python implementation."""

        self.abi_tag = abi_tag
        """ The ABI tag, following the PEP425 format, except that no ABI
        is sorted as None."""

        self.runtime_dependencies = tuple(dependencies.runtime)
        """ List of runtime dependencies (as strings)."""

        if metadata_version_info is None:
            metadata_version_info = _metadata_version_to_tuple(
                _METADATA_DEFAULT_VERSION
            )
        self.metadata_version_info = metadata_version_info
        """ The version format of the underlying metadata."""

        self.pkg_info = pkg_info
        """ A PackageInfo instance modeling the underlying PKG-INFO. May
        be None for eggs without an PKG-INFO file."""

        self.summary = summary
        """ The summary string."""

    @property
    def abi_tag_string(self):
        if self.abi_tag is None:
            return 'none'
        else:
            return self.abi_tag

    @property
    def build(self):
        """ The build number."""
        return self.version.build

    @property
    def egg_basename(self):
        """ The egg "base name", i.e. the name part of the egg filename."""
        return self._raw_name

    @property
    def egg_name(self):
        """ The egg filename."""
        return self._spec_depend.egg_name

    @property
    def kind(self):
        return "egg"

    @property
    def name(self):
        """ The package name."""
        return self._raw_name.lower().replace("-", "_")

    @property
    def platform_tag(self):
        """ Platform tag following PEP425, except that no platform is
        represented as None and not 'any'."""
        if self.platform is None:
            return None
        else:
            return self.platform.pep425_tag

    @property
    def platform_tag_string(self):
        if self.platform_tag is None:
            return 'any'
        else:
            return self.platform_tag

    @property
    def python_tag(self):
        if self.python is None:
            return None
        else:
            return self.python.pep425_tag

    @property
    def python_tag_string(self):
        if self.python_tag is None:
            # an extension of PEP 425, to signify the egg will work on any
            # python version (mostly non-python eggs)
            return 'none'
        else:
            return self.python_tag

    @property
    def spec_depend_string(self):
        return self._spec_depend.to_string()

    @property
    def upstream_version(self):
        return str(self.version.upstream)

    @property
    def _python(self):
        if self.python is None:
            return None
        else:
            return "{0}.{1}".format(self.python.major, self.python.minor)

    @property
    def _spec_depend(self):
        if self.platform is None:
            _epd_legacy_platform = None
        else:
            _epd_legacy_platform = LegacyEPDPlatform(self.platform)

        args = {
            "name": self._raw_name,
            "version": self.upstream_version,
            "build": self.build,
            "python": self._python,
            "python_tag": self.python_tag,
            "abi_tag": self.abi_tag,
            "platform_tag": self.platform_tag,
            "packages": [p for p in self.runtime_dependencies],
            "_epd_legacy_platform": _epd_legacy_platform,
            "_metadata_version": ".".join(
                str(i) for i in self.metadata_version_info
            ),
        }
        return LegacySpecDepend(**args)
