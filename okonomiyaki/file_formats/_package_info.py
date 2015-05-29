"""
Most of the code below is adapted from pkg-info 1.2.1

We support only 1.0 and 1.1, as 1.2 does not seem to be used anywhere ?
"""
import six
import zipfile2

from six.moves import StringIO

from ..errors import OkonomiyakiError


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

HEADER_ATTRS = {
    '1.0': HEADER_ATTRS_1_0,
    '1.1': HEADER_ATTRS_1_1,
}


class PackageInfo(object):
    """ Class modeling the PKG-INFO content.
    """
    @classmethod
    def from_egg(cls, path_or_file):
        """ Create a PackageInfo instance from an existing egg.

        Parameters
        ----------
        path: str or file-like object.
            If a string, understood as the path to the egg. Otherwise,
            understood as a zipfile-like object.
        """
        if isinstance(path_or_file, six.string_types):
            with zipfile2.ZipFile(path_or_file) as fp:
                for candidate in _PKG_INFO_CANDIDATES:
                    try:
                        data = fp.read(candidate)
                        break
                    except KeyError:
                        pass
                else:
                    msg = "No PKG-INFO metadata found"
                    raise OkonomiyakiError(msg)
        else:
            data = path_or_file.read(_PKG_INFO_LOCATION)
        return cls.from_string(data.decode(PKG_INFO_ENCODING))

    @classmethod
    def from_string(cls, s):
        fp = StringIO(_must_decode(s))
        msg = _parse(fp)

        kw = {}

        if 'Metadata-Version' in msg:
            metadata_version = _get(msg, 'Metadata-Version')
        else:
            metadata_version = "1.0"

        for header_name, attr_name, multiple in \
                _get_header_attributes(metadata_version):
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
                 author_email="", license="", classifiers=None,
                 requires=None, provides=None, obsoletes=None):
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

    def to_string(self, metadata_version_info=(1, 2)):
        s = StringIO()
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

    def _write_field(self, s, name, value):
        value = '%s: %s\n' % (name, value)
        s.write(value)

    def _write_list(self, s, name, values):
        for value in values:
            self._write_field(s, name, value)


def _get_header_attributes(metadata_version):
    attributes = HEADER_ATTRS.get(metadata_version)
    if attributes is None:
        msg = ("Unsupported PKG-INFO metadata format: {0!r}"
               .format(metadata_version))
        raise OkonomiyakiError(msg)
    else:
        return attributes


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


# Copied from distutils.util
def _rfc822_escape(header):
    """Return a version of the string escaped for inclusion in an
    RFC-822 header, by ensuring there are 8 spaces space after each newline.
    """
    lines = header.split('\n')
    header = ('\n' + 8*' ').join(lines)
    return header
