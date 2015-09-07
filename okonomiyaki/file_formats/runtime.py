import os.path
import json

import six
import zipfile2

from attr import attr, attributes
from attr.validators import instance_of

from okonomiyaki.errors import InvalidMetadata, UnsupportedMetadata
from okonomiyaki.platforms import EPDPlatform, Platform
from okonomiyaki.versions import MetadataVersion, SemanticVersion


RuntimeVersion = SemanticVersion

_METADATA_ARCNAME = "metadata/runtime.json"


@attributes
class RuntimeMetadataV1(object):
    """ The metadata of a runtime package (i.e. the actual zipfile containing
    the runtime code).

    This is a base class, do not instantiate directly.
    """
    language = attr(validator=instance_of(six.text_type))
    "The language (e.g. 'python')"

    implementation = attr(validator=instance_of(six.text_type))
    "The implementation (e.g. 'cpython')"

    version = attr(validator=instance_of(RuntimeVersion))
    "The full version (upstream + build)"

    platform = attr(validator=instance_of(Platform))
    "The platform on which this runtime may run."

    build_revision = attr(validator=instance_of(six.text_type))
    """The internal version. Informative only, has no semantices and my be
    empty."""

    executable = attr(validator=instance_of(six.text_type))
    """Executable path. May be a templated variable.
    """

    paths = attr(validator=instance_of(tuple))
    """Directories to add to $PATH to have access to this runtime."""

    post_install = attr(validator=instance_of(tuple))
    """Command to execute as part of post installation."""

    @classmethod
    def from_path(cls, path_or_file):
        if isinstance(path_or_file, six.string_types):
            # We don't use the parsed metadata here, but that allows us to
            # sanity check against old runtimes
            _parse_from_path(path_or_file)
            with zipfile2.ZipFile(path_or_file) as zp:
                metadata_s = _read_runtime_metadata_json(zp)
        else:
            metadata_s = _read_runtime_metadata_json(path_or_file)

        metadata_dict = json.loads(metadata_s)

        metadata_version = metadata_dict["metadata_version"]
        if metadata_version != "1.0":
            msg = "Unsupported metadata version: {0!r}"
            raise UnsupportedMetadata(msg.format(metadata_version))

        return cls.from_json_dict(metadata_dict)

    @classmethod
    def from_json_dict(cls, data):
        args = cls._from_json_dict(data)
        return cls(*args)

    @classmethod
    def _from_json_dict(cls, data):
        language = data["language"]
        implementation = data["implementation"]
        version = RuntimeVersion.from_string(data["version"])
        platform = EPDPlatform.from_epd_string(data["platform"]).platform

        build_revision = data["build_revision"]

        executable = data["executable"]
        paths = tuple(data["paths"])
        post_install = tuple(data["post_install"])

        return (
            language, implementation, version, platform, build_revision,
            executable, paths, post_install
        )

    @property
    def filename(self):
        disp_platform = EPDPlatform(self.platform).platform_name
        disp_platform += "_" + str(self.platform.arch)
        template = "{0.language}-{0.implementation}-{0.version}-{1}"
        return template.format(self, disp_platform) + ".runtime"


class JuliaRuntimeMetadataV1(RuntimeMetadataV1):
    """ Class representing the metadata of a julia runtime package.
    """


@attributes
class PythonRuntimeMetadataV1(RuntimeMetadataV1):
    """ Class representing the metadata of a python runtime package.
    """
    scriptsdir = attr(validator=instance_of(six.text_type))
    site_packages = attr(validator=instance_of(six.text_type))

    @classmethod
    def _from_json_dict(cls, data):
        args = super(PythonRuntimeMetadataV1, cls)._from_json_dict(data)
        scriptsdir = data["scriptsdir"]
        site_packages = data["site_packages"]
        return args + (scriptsdir, site_packages)


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
        return klass.from_path(path_or_file)


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
