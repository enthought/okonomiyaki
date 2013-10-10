from ..bundled.traitlets import HasTraits, Enum, Instance
from ..platform import EPD_PLATFORM_SHORT_NAMES

from .common import egg_name
from .enpkg import EnpkgS3IndexEntry


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

    enpkg_metadata = Instance(EnpkgS3IndexEntry)

    @property
    def repository_type(self):
        return self.enpkg_metadata.product

    @property
    def name(self):
        return self.enpkg_metadata.name

    @property
    def version(self):
        """The upstream version (not including the build number)."""
        return self.enpkg_metadata.version

    @property
    def build(self):
        return self.enpkg_metadata.build

    @property
    def egg_name(self):
        """The egg filename."""
        return egg_name(self.enpkg_metadata.egg_basename, self.version,
                        self.build)

    @property
    def grits_key(self):
        return "enthought/eggs/{0}/{1}".format(self.platform, self.egg_name)

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
        ret = self.enpkg_metadata.to_dict()
        ret["platform"] = self.platform
        return ret

    @classmethod
    def from_egg(cls, path, platform, repository_type="commercial"):
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

        return cls(platform=platform, enpkg_metadata=enpkg_metadata)
