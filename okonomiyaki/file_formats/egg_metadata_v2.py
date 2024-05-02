import six
import zipfile2

from attr import Factory, attributes, attr
from attr.validators import instance_of, optional

from okonomiyaki.platforms import (
    EPDPlatform, PlatformABI, PythonABI, PythonImplementation
)
from okonomiyaki.utils import compute_sha256
from okonomiyaki.versions import EnpkgVersion, MetadataVersion

from ._blacklist import (
    may_be_in_platform_blacklist, may_be_in_python_tag_blacklist,
    may_be_in_pkg_info_blacklist
)
from ._package_info import PackageInfo, _keep_position

from . import _egg_info


def text_attr(**kw):
    """ An attrs.attr-like descriptor to describe fields that must be unicode.
    """
    for k in ("validator", ):
        if k in kw:
            raise ValueError("Cannot pass '{0}' argument".format(k))
    return attr(validator=instance_of(six.text_type), **kw)


def dependency_type(inst, attr, value):
    if not isinstance(value, tuple):
        raise TypeError("Dependency must be a tuple")
    for item in value:
        if len(item) != 2:
            raise ValueError("Each dependency value must be a pair")
        name, disjunctions = item
        if not isinstance(name, six.text_type):
            raise ValueError(
                u"Expected a text type, got {!r}".format(name)
            )
        if not isinstance(disjunctions, tuple):
            raise ValueError(
                u"Expected tuples for disjunctions, got {!r}".format(disjunctions)
            )
        for disjunction in disjunctions:
            if isinstance(disjunction, tuple):
                for conjunction in disjunction:
                    if not isinstance(conjunction, six.text_type):
                        raise ValueError(
                            u"Expected conjunction to be a string, got {!r}"
                            .format(conjunction)
                        )
            else:
                raise ValueError(
                    u"Expected tuple for disjunction, got {!r}".format(disjunction)
                )


def dependency_attr(**kw):
    """ An attrs.attr-like descriptor to describe fields that must be
    dependency like, that is a tuple of (name, disjunctions) pairs, where each
    disjunction is a tuple of strings.
    """
    for k in ("validator", "default"):
        if k in kw:
            raise ValueError("Cannot pass '{0}' argument".format(k))
    return attr(validator=dependency_type, default=Factory(tuple))


def _convert_to_metadata_version(s):
    if isinstance(s, MetadataVersion):
        return s
    else:
        return MetadataVersion.from_string(s)


def _convert_to_enpkg_version(s):
    if isinstance(s, EnpkgVersion):
        return s
    else:
        return EnpkgVersion.from_string(s)


def _convert_to_epd_platform(s):
    if isinstance(s, EPDPlatform):
        return s
    elif isinstance(s, six.text_type):
        return EPDPlatform.from_string(s)
    else:
        return None


def _convert_to_python_implementation(s):
    if isinstance(s, PythonImplementation):
        return s
    elif isinstance(s, six.text_type):
        return PythonImplementation.from_string(s)
    else:
        return None


def _convert_to_python_abi(s):
    if isinstance(s, PythonABI):
        return s
    elif isinstance(s, six.text_type):
        return PythonABI(s)
    else:
        return None


def _convert_to_platform_abi(s):
    if isinstance(s, PlatformABI):
        return s
    elif isinstance(s, six.text_type):
        return PlatformABI(s)
    else:
        return None


def _convert_to_package_info(s):
    if isinstance(s, PackageInfo):
        return s
    elif isinstance(s, six.text_type):
        return PackageInfo.from_string(s)
    else:
        return None


@attributes
class EggMetadataV2(object):
    metadata_version = attr(
        validator=instance_of(MetadataVersion),
        convert=_convert_to_metadata_version,
    )

    _raw_name = text_attr()

    version = attr(
        validator=instance_of(EnpkgVersion), convert=_convert_to_enpkg_version
    )

    epd_platform = attr(
        validator=optional(instance_of(EPDPlatform)),
        convert=_convert_to_epd_platform,
    )

    python_implementation = attr(
        validator=optional(instance_of(PythonImplementation)),
        convert=_convert_to_python_implementation
    )

    python_abi = attr(
        validator=optional(instance_of(PythonABI)),
        convert=_convert_to_python_abi,
    )

    platform_abi = attr(
        validator=optional(instance_of(PlatformABI)), convert=_convert_to_platform_abi,
    )

    package_info = attr(
        validator=optional(instance_of(PackageInfo)), convert=_convert_to_package_info,
    )

    summary = text_attr()
    license = attr(validator=optional(instance_of(six.text_type)))

    runtime_dependencies = dependency_attr()

    build_dependencies = dependency_attr()
    test_dependencies = dependency_attr()
    conflicts = dependency_attr()
    provides = dependency_attr()

    @property
    def epd_platform_tag(self):
        if self.epd_platform is None:
            return None
        else:
            return str(self.epd_platform)

    @property
    def name(self):
        return self._raw_name.lower()

    @property
    def platform_abi_tag(self):
        if self.platform_abi is None:
            return None
        else:
            return self.platform_abi.pep425_tag

    @property
    def platform_abi_tag_string(self):
        return PlatformABI.pep425_tag_string(self.platform_abi)

    @property
    def platform_tag(self):
        """ Platform tag following PEP425, except that no platform is
        represented as None and not 'any'."""
        if self.epd_platform is None:
            return None
        else:
            return self.epd_platform.pep425_tag

    @property
    def platform_tag_string(self):
        return EPDPlatform.pep425_tag_string(self.epd_platform)

    @property
    def python_abi_tag(self):
        if self.python_abi is None:
            return None
        else:
            return self.python_abi.pep425_tag

    @property
    def python_abi_tag_string(self):
        return PythonABI.pep425_tag_string(self.python_abi)

    @property
    def python_tag(self):
        if self.python_implementation is None:
            return None
        else:
            return self.python_implementation.pep425_tag

    @property
    def python_tag_string(self):
        return PythonImplementation.pep425_tag_string(self.python_implementation)

    @staticmethod
    def _may_be_in_blacklist(path):
        return (
            may_be_in_platform_blacklist(path)
            or may_be_in_pkg_info_blacklist(path)
            or may_be_in_python_tag_blacklist(path)
        )

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
        if isinstance(path_or_file, six.string_types):
            if cls._may_be_in_blacklist(path_or_file):
                sha256 = compute_sha256(path_or_file)
        else:
            with _keep_position(path_or_file.fp):
                sha256 = compute_sha256(path_or_file.fp)
        return cls._from_egg(path_or_file, sha256, strict)

    @classmethod
    def _from_egg(cls, path_or_file, sha256, strict=True):
        v1_arcname = "EGG-INFO/spec/depend"

        def _read(zp):
            try:
                with _keep_position(zp.fp):
                    zp.read(v1_arcname)
            except KeyError:
                raise NotImplementedError()
            else:
                return cls._from_v1_egg_metadata(
                    _egg_info.EggMetadata._from_egg(zp, sha256, strict)
                )

        if isinstance(path_or_file, six.string_types):
            with zipfile2.ZipFile(path_or_file) as zp:
                return _read(zp)
        else:
            return _read(path_or_file)

    @classmethod
    def _from_v1_egg_metadata(cls, m):
        if m._pkg_info is not None:
            license = m.pkg_info.license
        else:
            license = None
        return cls(
            m.metadata_version, m._raw_name, m.version, m.platform, m.python,
            m.abi, m.platform_abi, m._pkg_info, m.summary, license,
            runtime_dependencies=_convert_requirement_to_dependencies(m.runtime_dependencies),
        )


def _convert_requirement_to_dependencies(requirements):
    def _transformer(entry):
        if len(entry.version_string) == 0:
            return (entry.name, ((u"*",),))
        elif entry.build_number == -1:
            return (
                entry.name,
                ((u"^= {}".format(entry.version_string),),)
            )
        else:
            return (
                entry.name,
                ((u"== {}-{}".format(entry.version_string, entry.build_number),),)
            )

    return tuple(_transformer(entry) for entry in requirements)
