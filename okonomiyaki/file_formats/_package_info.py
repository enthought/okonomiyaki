"""
Most of the code below is adapted from pkg-info 1.2.1

We support 1.0, 1.1, 1.2 and 2.0.
"""
import contextlib
import os.path

import zipfile2

from ..utils import py3compat, compute_sha256
from ..errors import OkonomiyakiError

from ._blacklist import EGG_PKG_INFO_BLACK_LIST, may_be_in_pkg_info_blacklist
from ._wheel_info import WheelInfo


_PKG_INFO_LOCATION = "EGG-INFO/PKG-INFO"
_PKG_INFO_CANDIDATES = (
    _PKG_INFO_LOCATION,
    "EGG-INFO/PKG-INFO.bak",
)

PKG_INFO_ENCODING = 'utf-8'

HEADER_ATTRS_1_0 = (  # PEP 241
    ('Metadata-Version', 'metadata_version', False),
    ('Name', 'name', False),
    ('Version', 'version', False),
    ('Platform', 'platforms', True),
    ('Supported-Platform', 'supported_platforms', True),
    ('Summary', 'summary', False),
    ('Description', 'description', False),
    ('Keywords', 'keywords', False),
    ('Home-Page', 'home_page', False),
    ('Author', 'author', False),
    ('Author-email', 'author_email', False),
    ('License', 'license', False),
)

HEADER_ATTRS_1_1 = HEADER_ATTRS_1_0 + (  # PEP 314
    ('Classifier', 'classifiers', True),
    ('Download-URL', 'download_url', False),
    ('Requires', 'requires', True),
    ('Provides', 'provides', True),
    ('Obsoletes', 'obsoletes', True),
)

HEADER_ATTRS_1_2 = HEADER_ATTRS_1_1 + (  # PEP 345
    ('Maintainer', 'maintainer', False),
    ('Maintainer-email', 'maintainer_email', False),
    ('Requires-Python', 'requires_python', False),
    ('Requires-External', 'requires_external', True),
    ('Requires-Dist', 'requires_dist', True),
    ('Provides-Dist', 'provides_dist', True),
    ('Obsoletes-Dist', 'obsoletes_dist', True),
    ('Project-URL', 'project_urls', True),
)

# 2.0 not formalized, but seen in wheels produced by wheel as recent as 0.30.0.
# See PEP 426, and the PyPI pkginfo project.
HEADER_ATTRS_2_0 = HEADER_ATTRS_1_2

HEADER_ATTRS = {
    (1, 0): HEADER_ATTRS_1_0,
    (1, 1): HEADER_ATTRS_1_1,
    (1, 2): HEADER_ATTRS_1_2,
    (2, 0): HEADER_ATTRS_2_0,
}

MAX_SUPPORTED_VERSION = max(HEADER_ATTRS.keys())


class PackageInfo(object):
    """ Class modeling the PKG-INFO content.
    """
    @classmethod
    def from_path(cls, path, strict=True):
        if path.endswith(".egg"):
            return cls.from_egg(path, strict)
        elif path.endswith(".whl"):
            return cls.from_wheel(path, strict)
        else:
            raise OkonomiyakiError(
                u"Unrecognized package extension: '{}'".format(
                    os.path.splitext(path)[1]
                )
            )

    @classmethod
    def from_wheel(cls, path_or_file, strict=True):
        if isinstance(path_or_file, py3compat.string_types):
            wheel_info = WheelInfo.from_path(path_or_file)

            with zipfile2.ZipFile(path_or_file) as fp:
                data = _read_pkg_info_wheel(fp, (wheel_info.name, wheel_info.version))
        else:
            # path_or_file assumed to be a ZipFile instance
            data = _read_pkg_info_wheel(path_or_file)

        if data is None:
            msg = "No METADATA archive found in wheel file"
            raise OkonomiyakiError(msg)

        data = _convert_if_needed(data, None, strict)
        return cls.from_string(data)

    @classmethod
    def from_egg(cls, path_or_file, strict=True):
        """ Create a PackageInfo instance from an existing egg.

        Parameters
        ----------
        path: str or file-like object.
            If a string, understood as the path to the egg. Otherwise,
            understood as a zipfile-like object.
        """
        sha256 = None
        if isinstance(path_or_file, py3compat.string_types):
            if may_be_in_pkg_info_blacklist(path_or_file):
                sha256 = compute_sha256(path_or_file)
        else:
            with _keep_position(path_or_file.fp):
                sha256 = compute_sha256(path_or_file.fp)
        return cls._from_egg(path_or_file, sha256, strict)

    @classmethod
    def _from_egg(cls, path_or_file, sha256, strict=True):
        if isinstance(path_or_file, py3compat.string_types):
            with zipfile2.ZipFile(path_or_file) as fp:
                data = _read_pkg_info(fp)
        else:
            data = _read_pkg_info(path_or_file)

        if data is None:
            msg = "No PKG-INFO metadata found"
            raise OkonomiyakiError(msg)

        data = _convert_if_needed(data, sha256, strict)
        return cls.from_string(data)

    @classmethod
    def from_string(cls, s):
        if not isinstance(s, py3compat.text_type):
            raise ValueError("Expected text value, got {0!r}".format(type(s)))
        fp = py3compat.StringIO(s)
        msg = _parse(fp)

        kw = {}

        if 'Metadata-Version' in msg:
            metadata_version = _get(msg, 'Metadata-Version')
        else:
            metadata_version = "1.0"

        _ensure_supported_version(metadata_version)
        metadata_version_info = _string_to_version_info(metadata_version)
        attributes = HEADER_ATTRS[metadata_version_info]

        for header_name, attr_name, multiple in attributes:
            if attr_name == 'metadata_version':
                continue

            if header_name in msg:
                if header_name == "Keywords":
                    if msg != "UNKNOWN":
                        value = _collapse_leading_ws(header_name,
                                                     msg.get(header_name))
                        kw[attr_name] = tuple(value.split())
                elif multiple:
                    values = _get_all(msg, header_name)
                    if values != ["UNKNOWN"]:
                        kw[attr_name] = values
                else:
                    value = _get(msg, header_name)
                    if value != 'UNKNOWN':
                        kw[attr_name] = value

        name = kw.pop("name")
        version = kw.pop("version")
        return cls(metadata_version, name, version, **kw)

    def __init__(self, metadata_version, name, version, platforms=None,
                 supported_platforms=None, summary="", description="",
                 keywords=None, home_page="", download_url="", author="",
                 author_email="", license="", classifiers=None, requires=None,
                 provides=None, obsoletes=None, maintainer="",
                 maintainer_email="", requires_python=None,
                 requires_external=None, requires_dist=None,
                 provides_dist=None, obsoletes_dist=None, projects_urls=None):
        _ensure_supported_version(metadata_version)

        self.metadata_version = metadata_version

        # version 1.0
        self.name = name
        self.version = version
        self.platforms = platforms or ()
        self.supported_platforms = supported_platforms or ()
        self.summary = summary
        self.description = description
        self.keywords = keywords or ()
        self.home_page = home_page
        self.download_url = download_url
        self.author = author
        self.author_email = author_email
        self.license = license

        # version 1.1
        self.classifiers = classifiers or ()
        self.requires = requires or ()
        self.provides = provides or ()
        self.obsoletes = obsoletes or ()

        # version 1.2
        self.maintainer = maintainer or ""
        self.maintainer_email = maintainer_email or ""
        self.requires_python = requires_python or ()
        self.requires_external = requires_external or ()
        self.requires_dist = requires_dist or ()
        self.provides_dist = provides_dist or ()
        self.obsoletes_dist = obsoletes_dist or ()
        self.project_urls = projects_urls or ()

    def to_string(self, metadata_version_info=MAX_SUPPORTED_VERSION):
        s = py3compat.StringIO()
        self._write_field(s, 'Metadata-Version', self.metadata_version)
        self._write_field(s, 'Name', self.name)
        self._write_field(s, 'Version', self.version)
        self._write_field(s, 'Summary', self.summary)
        self._write_field(s, 'Home-page', self.home_page)
        self._write_field(s, 'Author', self.author)
        self._write_field(s, 'Author-email', self.author_email)
        self._write_field(s, 'License', self.license)
        if metadata_version_info >= (1, 1):
            if self.download_url:
                self._write_field(s, 'Download-URL', self.download_url)

        description = _rfc822_escape(self.description)
        self._write_field(s, 'Description', description)

        keywords = ' '.join(self.keywords)
        if keywords:
            self._write_field(s, 'Keywords', keywords)

        if len(self.platforms) == 0:
            self._write_list(s, 'Platform', ("UNKNOWN",))
        else:
            self._write_list(s, 'Platform', self.platforms)

        if metadata_version_info >= (1, 1):
            self._write_list(s, 'Classifier', self.classifiers)

            self._write_list(s, 'Requires', self.requires)
            self._write_list(s, 'Provides', self.provides)
            self._write_list(s, 'Obsoletes', self.obsoletes)

        return s.getvalue()

    def _dump_as_zip(self, zp, metadata_version_info=MAX_SUPPORTED_VERSION):
        zp.writestr(
            _PKG_INFO_LOCATION,
            self.to_string(metadata_version_info).encode(PKG_INFO_ENCODING)
        )

    def _write_field(self, s, name, value):
        value = '%s: %s\n' % (name, value)
        s.write(value)

    def _write_list(self, s, name, values):
        for value in values:
            self._write_field(s, name, value)

    # Protocol implementations
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.metadata_version == other.metadata_version and
                self.to_string() == other.to_string()
            )
        elif other is None:
            # We special-case None because EggMetadata.pkg_info may be None,
            # and we want to support foo.pkg_info == foo2.pkg_info when one may
            # be None
            return False
        else:
            raise TypeError(
                "Only equality between PackageInfo instances is supported"
            )

    def __ne__(self, other):
        return not self == other


def _string_to_version_info(metadata_version):
    return tuple(int(i) for i in metadata_version.split("."))


def _ensure_supported_version(metadata_version):
    metadata_version_info = _string_to_version_info(metadata_version)
    if metadata_version_info not in HEADER_ATTRS:
        msg = ("Unsupported PKG-INFO metadata format: {0!r}"
               .format(metadata_version))
        raise OkonomiyakiError(msg)


def _parse(fp):
    from email.parser import Parser
    return Parser().parse(fp)


def _must_decode(value):  # pragma NO COVER
    if type(value) is bytes:
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin1')
    return value


def _get(msg, header):
    return _collapse_leading_ws(header, msg.get(header))


def _get_all(msg, header):
    return [_collapse_leading_ws(header, x) for x in msg.get_all(header)]


def _collapse_leading_ws(header, txt):
    """
    ``Description`` header must preserve newlines; all others need not
    """
    if header.lower() == 'description':  # preserve newlines
        lines = [x[8:] if x.startswith(' ' * 8) else x
                 for x in txt.strip().splitlines()]
        # Append a line to be char-by-char compatible with distutils
        lines.append('')
        return '\n'.join(lines)
    else:
        return ' '.join([x.strip() for x in txt.splitlines()])


def _convert_if_needed(data, sha256, strict):
    """ sha256 may be None, in which case it is assumed no special handling
    through black list is needed.
    """
    decoded_data = EGG_PKG_INFO_BLACK_LIST.get(sha256)
    if decoded_data is None:
        if strict:
            return data.decode(PKG_INFO_ENCODING)
        else:
            return data.decode(PKG_INFO_ENCODING, 'replace')
    else:
        return decoded_data


def _read_pkg_info_wheel(fp, name_version=None):
    """ Read the METADATA content in the possible locations for a wheel, and
    return the decoded content.

    If no pkg info data is found, return None.

    Parameters
    ----------
    fp : ZipFile
    name_or_version: tuple or None
        If not None, assumed to be (name, version) pair. If known,
        significantly speed up finding the metadata archive name.
    """
    if name_version is None:
        for arcname in fp.namelist():
            parts = arcname.split("/")
            if (
                len(parts) == 2 and
                parts[0].endswith(".dist-info") and
                parts[1] == "METADATA"
            ):
                candidate = arcname
                break
        else:
            return None
    else:
        name, version = name_version
        dist_info = "{0}-{1}.dist-info".format(name, version)
        candidate = "{0}/METADATA".format(dist_info)

    try:
        return fp.read(candidate)
    except KeyError:
        return None


def _read_pkg_info(fp):
    """ Read the PKG-INFO content in the possible locations, and return
    the decoded content.

    If no PKG-INFO is found, return None.
    """
    for candidate in _PKG_INFO_CANDIDATES:
        try:
            return fp.read(candidate)
        except KeyError:
            pass
    return None


@contextlib.contextmanager
def _keep_position(fp):
    pos = fp.tell()
    try:
        fp.seek(0)
        yield
    finally:
        fp.seek(pos)


# Copied from distutils.util
def _rfc822_escape(header):
    """Return a version of the string escaped for inclusion in an
    RFC-822 header, by ensuring there are 8 spaces space after each newline.
    """
    lines = header.split('\n')
    header = ('\n' + 8 * ' ').join(lines)
    return header
