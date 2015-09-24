from __future__ import absolute_import

import abc
import os.path
import json

import jsonschema
import six
import zipfile2

from attr import attr, attributes
from attr.validators import instance_of

from ..errors import InvalidMetadata, UnsupportedMetadata
from ..platforms import EPDPlatform, Platform
from ..versions import MetadataVersion, RuntimeVersion

from .common import _platform_string
from .runtime_schemas import _JULIA_V1, _PYTHON_V1


_METADATA_ARCNAME = "enthought/runtime.json"


@attributes
class IRuntimeMetadata(six.with_metaclass(abc.ABCMeta)):
    """ The metadata of a runtime package (i.e. the actual zipfile containing
    the runtime code).
    """
    metadata_version = attr(validator=instance_of(MetadataVersion))

    @classmethod
    def factory_from_path(cls, path):
        """ Creates a metadata instance from the given path.

        The created instance's class will be detected dynamically from the
        metadata file content.
        """
        return runtime_metadata_factory(path)

    @classmethod
    @abc.abstractmethod
    def _from_path(cls, path):
        """Create an instance of the given runtime metadata class from a
        path.

        Users of the metadata classes should not use this method directly, but
        use the factory class method instead."""

    @abc.abstractproperty
    def filename(self):
        """The filename a runtime with this set of metadata."""


@attributes
class IRuntimeMetadataV1(IRuntimeMetadata):
    """ The metadata of a runtime package (i.e. the actual zipfile containing
    the runtime code).
    """
    # Note: the attributes in IRuntimeMetadataV1 need to be synchronized with
    # IRuntimeInfoV1
    language = attr(validator=instance_of(six.text_type))
    "The language (e.g. 'python')"

    implementation = attr(validator=instance_of(six.text_type))
    "The implementation (e.g. 'cpython')"

    version = attr(validator=instance_of(RuntimeVersion))
    """The implementation version, e.g. pypy 2.6.1 would report 2.6.1 as the
    'upstream' part."""

    language_version = attr(validator=instance_of(RuntimeVersion))
    """This is the 'language' version, e.g.  pypy 2.6.1 would report 2.7.10
    here."""

    platform = attr(validator=instance_of(Platform))
    "The platform on which this runtime may run."

    build_revision = attr(validator=instance_of(six.text_type))
    """The internal version. Informative only, has no semantices and may be
    empty."""

    executable = attr(validator=instance_of(six.text_type))
    """Executable path. May be a templated variable.
    """

    paths = attr(validator=instance_of(tuple))
    """Directories to add to $PATH to have access to this runtime."""

    post_install = attr(validator=instance_of(tuple))
    """Command to execute as part of post installation."""

    _json_schema = None

    @classmethod
    def _from_path(cls, path_or_file):
        if isinstance(path_or_file, six.string_types):
            # We don't use the parsed metadata here, but that allows us to
            # sanity check against old runtimes
            _parse_from_path(path_or_file)
            with zipfile2.ZipFile(path_or_file) as zp:
                metadata_s = _read_runtime_metadata_json(zp)
        else:
            metadata_s = _read_runtime_metadata_json(path_or_file)

        metadata_dict = json.loads(metadata_s)
        try:
            jsonschema.validate(metadata_dict, cls._json_schema)
        except jsonschema.ValidationError as e:
            msg = "Invalid metadata: {0!r}".format(e.message)
            raise InvalidMetadata(msg)

        metadata_version = metadata_dict["metadata_version"]
        if metadata_version != "1.0":
            msg = "Unsupported metadata version: {0!r}"
            raise UnsupportedMetadata(msg.format(metadata_version))

        return cls._from_json_dict(metadata_dict)

    @classmethod
    def _from_json_dict(cls, data):
        args = cls._from_json_dict_impl(data)
        return cls(*args)

    @classmethod
    def _from_json_dict_impl(cls, data):
        metadata_version = MetadataVersion.from_string(
            data["metadata_version"]
        )
        language = data["language"]
        implementation = data["implementation"]
        version = RuntimeVersion.from_string(data["version"])
        language_version = RuntimeVersion.from_string(data["language_version"])
        platform = EPDPlatform.from_epd_string(data["platform"]).platform

        build_revision = data["build_revision"]

        executable = data["executable"]
        paths = tuple(data["paths"])
        post_install = tuple(data["post_install"])

        return (
            metadata_version, language, implementation, version,
            language_version, platform, build_revision, executable, paths,
            post_install
        )

    @property
    def filename(self):
        template = "{0.language}-{0.implementation}-{0.version}-{1}.runtime"
        return template.format(self, _platform_string(self.platform))


class JuliaRuntimeMetadataV1(IRuntimeMetadataV1):
    """ Class representing the metadata of a julia runtime package.
    """
    _json_schema = _JULIA_V1


@attributes
class PythonRuntimeMetadataV1(IRuntimeMetadataV1):
    """ Class representing the metadata of a python runtime package.
    """
    scriptsdir = attr(validator=instance_of(six.text_type))
    site_packages = attr(validator=instance_of(six.text_type))
    python_tag = attr(validator=instance_of(six.text_type))

    _json_schema = _PYTHON_V1

    @classmethod
    def _from_json_dict_impl(cls, data):
        args = super(PythonRuntimeMetadataV1, cls)._from_json_dict_impl(data)
        scriptsdir = data["scriptsdir"]
        site_packages = data["site_packages"]
        python_tag = data["python_tag"]
        return args + (scriptsdir, site_packages, python_tag)


_METADATA_KLASS_FACTORY = {
    (MetadataVersion.from_string("1.0"), "python"): PythonRuntimeMetadataV1,
    (MetadataVersion.from_string("1.0"), "julia"): JuliaRuntimeMetadataV1,
}


def runtime_metadata_factory(path_or_file):
    """ Creates metadata object of the appropriate class from the given path.

    Parameters
    ----------
    path_or_file: str or ZipFile
        The path to the runtime package. May be a ZipFile instance.
    """
    def _factory_key_from_metadata(json_dict):
        return (
            MetadataVersion.from_string(json_dict["metadata_version"]),
            json_dict["language"]
        )

    if isinstance(path_or_file, six.string_types):
        with zipfile2.ZipFile(path_or_file) as zp:
            metadata = _read_runtime_metadata_json(zp)
    else:
        metadata = _read_runtime_metadata_json(path_or_file)

    json_dict = json.loads(metadata)
    key = _factory_key_from_metadata(json_dict)
    klass = _METADATA_KLASS_FACTORY.get(key)
    if klass is None:
        msg = "No support for {0!r} combination".format(key)
        raise UnsupportedMetadata(msg)
    else:
        return klass._from_path(path_or_file)


def is_runtime_path_valid(path):
    """ Returns True if the given path is a valid runtime path, False
    otherwise.
    """
    try:
        _parse_from_path(path)
        return True
    except InvalidMetadata:
        return False


def _parse_from_path(path):
    filename = os.path.basename(path)
    base, ext = os.path.splitext(filename)

    if not ext == ".runtime":
        raise InvalidMetadata("Invalid extension: {0!r}".format(ext))

    parts = base.split("-", 2)
    if len(parts) != 3:
        raise InvalidMetadata("Invalid format: {0!r}".format(filename))

    language, implementation, remain = parts
    subparts = remain.rsplit("-", 1)

    if len(subparts) != 2:
        raise InvalidMetadata("Invalid format: {0!r}".format(filename))

    version_string, platform_string = subparts

    version = RuntimeVersion.from_string(version_string)
    epd_platform = EPDPlatform.from_epd_string(platform_string)

    return language, implementation, version, epd_platform.platform


def _read_runtime_metadata_json(zp):
    try:
        return zp.read(_METADATA_ARCNAME).decode()
    except KeyError:
        msg = "Invalid runtime (missing metadata archive {0!r} in runtime)"
        raise InvalidMetadata(msg.format(_METADATA_ARCNAME))
