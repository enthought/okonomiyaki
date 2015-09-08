from __future__ import absolute_import

import abc

import six

from attr import asdict, attr, attributes
from attr.validators import instance_of

from okonomiyaki.errors import UnsupportedMetadata
from okonomiyaki.platforms import Platform
from okonomiyaki.utils import substitute_variable, substitute_variables
from okonomiyaki.versions import MetadataVersion

from .common import RuntimeVersion, _platform_string
from .runtime_metadata import JuliaRuntimeMetadataV1, PythonRuntimeMetadataV1


@attributes
class IRuntimeInfoV1(six.with_metaclass(abc.ABCMeta)):
    metadata_version = attr(validator=instance_of(MetadataVersion))

    # Note: the attributes in IRuntimeInfoV1 need to be synchronized with
    # IRuntimeMetadataV1
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

    prefix = attr(validator=instance_of(six.text_type))
    """ Full path to the installed prefix."""

    name = attr(validator=instance_of(six.text_type))

    _metadata_klass = None

    @classmethod
    def from_json_dict(cls, data):
        metadata = cls._metadata_klass.from_json_dict(data)
        return cls.from_metadata(
            metadata, data["prefix"], data["name"]
        )

    @classmethod
    def from_metadata(cls, metadata, prefix, name):
        return cls(*cls._from_metadata(metadata, prefix, name))

    @classmethod
    def _from_metadata(cls, metadata, prefix, name):
        language = metadata.language
        implementation = metadata.implementation
        version = metadata.version
        platform = metadata.platform
        build_revision = metadata.build_revision

        variables = _compute_variables(metadata, prefix, name)

        executable = substitute_variable(metadata.executable, variables)

        paths = tuple(
            substitute_variable(path, variables) for path in metadata.paths
        )
        post_install = tuple(
            substitute_variable(part, variables)
            for part in metadata.post_install
        )

        return (
            MetadataVersion.from_string("1.0"), language, implementation,
            version, platform, build_revision, executable, paths, post_install,
            prefix, name
        )

    def to_json_dict(self):
        data_dict = asdict(self)
        for k in ("version", "metadata_version"):
            data_dict[k] = str(data_dict[k])
        data_dict["platform"] = _platform_string(self.platform)

        return data_dict


class JuliaRuntimeInfoV1(IRuntimeInfoV1):
    """ Class representing the metadata of an installed julia runtime.
    """
    _metadata_klass = JuliaRuntimeMetadataV1


@attributes
class PythonRuntimeInfoV1(IRuntimeInfoV1):
    """ Class representing the metadata of an installed python runtime.
    """
    scriptsdir = attr(validator=instance_of(six.text_type))
    site_packages = attr(validator=instance_of(six.text_type))

    _metadata_klass = PythonRuntimeMetadataV1

    @classmethod
    def _from_metadata(cls, metadata, prefix, name):
        args = super(PythonRuntimeInfoV1, cls)._from_metadata(
            metadata, prefix, name
        )
        variables = _compute_variables(metadata, prefix, name)
        scriptsdir = substitute_variable(metadata.scriptsdir, variables)
        site_packages = substitute_variable(metadata.site_packages, variables)

        return args + (scriptsdir, site_packages)

    def to_json_dict(self):
        json_dict = super(PythonRuntimeInfoV1, self).to_json_dict()
        for k in ("scriptsdir", "site_packages"):
            json_dict[k] = json_dict[k]

        return json_dict


_RUNTIME_INFO_JSON_FACTORY = {
    (MetadataVersion.from_string("1.0"), "python"): PythonRuntimeInfoV1,
    (MetadataVersion.from_string("1.0"), "julia"): JuliaRuntimeInfoV1,
}


def runtime_info_from_json(json_data):
    """ Create a runtime info instance from its json serialized state.
    """
    metadata_version = MetadataVersion.from_string(
        json_data["metadata_version"]
    )
    language = json_data["language"]
    key = (metadata_version, language)
    klass = _RUNTIME_INFO_JSON_FACTORY.get(key)
    if klass is None:
        msg = "Combination {0!r} is not supported".format(key)
        raise UnsupportedMetadata(msg)
    else:
        return klass.from_json_dict(json_data)


_RUNTIME_INFO_FACTORY = {}
for klass in (JuliaRuntimeInfoV1, PythonRuntimeInfoV1):
    _RUNTIME_INFO_FACTORY[klass._metadata_klass] = klass


def runtime_info_from_metadata(metadata, prefix, name):
    """ Create a runtime info instance from a runtime metadata instance, an
    (install) prefix and a runtime name.
    """
    klass = _RUNTIME_INFO_FACTORY.get(type(metadata))
    assert klass is not None
    return klass.from_metadata(metadata, prefix, name)


def _compute_variables(metadata, prefix, name):
    data = dict(
        (k.name, getattr(metadata, k.name)) for k in metadata.__attrs_attrs__
    )

    variables = dict(
        (k, v) for k, v in data.items() if isinstance(v, six.string_types)
    )
    variables["prefix"] = prefix
    variables["name"] = name

    return substitute_variables(variables, variables)
