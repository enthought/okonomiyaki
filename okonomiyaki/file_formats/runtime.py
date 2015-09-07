import os.path
import json

import six
import zipfile2

from attr import attr, attributes
from attr.validators import instance_of

from okonomiyaki.errors import InvalidMetadata, UnsupportedMetadata
from okonomiyaki.platforms import EPDPlatform, Platform
from okonomiyaki.versions import SemanticVersion


RuntimeVersion = SemanticVersion


@attributes
class RuntimeMetadataV1(object):
    """ The metadata of a runtime package (i.e. the actual zipfile containing
    the runtime code).
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
        def _read_metadata(zp):
            try:
                return zp.read("metadata/runtime.json").decode()
            except KeyError:
                msg = "Invalid runtime (missing metadata in runtime)"
                raise InvalidMetadata(msg)

        if isinstance(path_or_file, six.string_types):
            # We don't use the parsed metadata here, but that allows us to
            # sanity check against old runtimes
            _parse_from_path(path_or_file)
            with zipfile2.ZipFile(path_or_file) as zp:
                metadata_s = _read_metadata(zp)
        else:
            metadata_s = _read_metadata(path_or_file)

        metadata_dict = json.loads(metadata_s)

        metadata_version = metadata_dict["metadata_version"]
        if metadata_version != 1:
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
