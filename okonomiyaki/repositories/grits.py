from ..bundled.traitlets import HasTraits, Enum, Instance
from ..errors import OkonomiyakiError
from ..file_formats import egg_name, split_egg_name
from ..platforms.epd_platform import EPD_PLATFORM_SHORT_NAMES, EPDPlatform

from .enpkg import EnpkgS3IndexEntry

_DEFAULT_QA_LEVEL = "stable"


class GritsEggEntry(HasTraits):
    """
    This class models an egg entry metadata as required by Grits.

    Example
    -------
    >>> entry = GritsEggEntry.from_egg("numpy-1.7.1-1.egg", "rh5-32", "free")
    # Grits key, metadata and tags are available as simple properties
    >>> entry.grits_key
    >>> entry.grits_metadata
    >>> entry.grits_tags
    """
    platform = Enum(EPD_PLATFORM_SHORT_NAMES)

    qa_level = Enum(["stable", "staging", "ci"], _DEFAULT_QA_LEVEL)

    _enpkg_metadata = Instance(EnpkgS3IndexEntry)

    @property
    def repository_type(self):
        return self._enpkg_metadata.product

    @repository_type.setter
    def repository_type(self, value):
        self._enpkg_metadata.product = value

    @property
    def name(self):
        return self._enpkg_metadata.name

    @property
    def version(self):
        """The upstream version (not including the build number)."""
        return self._enpkg_metadata.version

    @property
    def build(self):
        return self._enpkg_metadata.build

    @property
    def egg_name(self):
        """The egg filename."""
        return egg_name(self._enpkg_metadata.egg_basename, self.version,
                        self.build)

    @property
    def grits_key(self):
        return "enthought/eggs/{0}/{1}".format(self.platform, self.egg_name)

    @property
    def python_version(self):
        return self._enpkg_metadata.python

    @property
    def grits_tags(self):
        tag_keys = ("accessible", "owned", "modifiable", "visible", "writable")
        if self.repository_type == "free":
            return dict((k, ["enthought-free"]) for k in tag_keys)
        elif self.repository_type == "commercial":
            tags = dict((k, ["enthought-commercial", "enthought-academic"])
                        for k in tag_keys)
            tags["visible"] = ["enthought-free"]
            return tags
        else:
            raise NotImplementedError(
                "Tags for repository type '{}' not implemented yet".
                format(self.repository))

    @property
    def grits_metadata(self):
        ret = self._enpkg_metadata.to_dict()
        ret["platform"] = self.platform
        ret["qa_level"] = self.qa_level
        ret.pop("available")
        return ret

    @classmethod
    def from_egg(cls, path, platform, repository_type="commercial",
                 qa_level=_DEFAULT_QA_LEVEL):
        """Create a GritsEggEntry from an egg package.

        Parameters
        ----------
        Parameters: str
            Path to the egg
        platform: str
            The consolidated platform (e.g. 'rh5-32')
        repository_type: str
            Type of repository: 'commercial' or 'free'
        """
        enpkg_metadata = EnpkgS3IndexEntry.from_egg(path, repository_type)

        return cls(
            platform=platform, qa_level=qa_level,
            _enpkg_metadata=enpkg_metadata
        )

    @classmethod
    def from_setuptools_egg(cls, path, platform=None):
        if platform is None:
            platform = EPDPlatform.from_running_system().short

        enpkg_metadata = EnpkgS3IndexEntry.from_setuptools_egg(path)
        return cls(platform=platform, _enpkg_metadata=enpkg_metadata)

    @classmethod
    def _from_grits_metadata(cls, data, platform):
        qa_level = data.pop("qa_level", _DEFAULT_QA_LEVEL)
        data.pop("name")
        enpkg_metadata = EnpkgS3IndexEntry.from_data(data)
        return cls(
            platform=platform, qa_level=qa_level,
            _enpkg_metadata=enpkg_metadata
        )

    @classmethod
    def from_key_and_metadata(cls, key, data):
        platform = _grits_egg_key_to_platform(key)
        data = data.copy()
        data.setdefault("egg_basename", _grits_egg_key_to_egg_basename(key))
        return cls._from_grits_metadata(data, platform)


def _grits_egg_key_to_platform(key):
    parts = key.split("/")
    return parts[2]


def _grits_egg_key_to_egg_basename(key):
    parts = key.split("/")
    egg_name = parts[-1]
    if not egg_name.endswith(".egg"):
        raise OkonomiyakiError("Invalid grits key for eggs: {}".format(key))
    else:
        return split_egg_name(egg_name)[0]
