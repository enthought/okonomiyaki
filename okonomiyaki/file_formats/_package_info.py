"""
Most of the code below is adapted from pkg-info 1.2.1

We support only 1.0 and 1.1, as 1.2 does not seem to be used anywhere ?
"""
from email.parser import Parser

import six
import zipfile2

from six.moves import StringIO


HEADER_ATTRS_1_0 = ( # PEP 241
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

HEADER_ATTRS_1_1 = HEADER_ATTRS_1_0 + ( # PEP 314
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
        pkg_info_path = "EGG-INFO/PKG-INFO"

        if isinstance(path_or_file, six.string_types):
            with zipfile2.ZipFile(path_or_file) as fp:
                data = fp.read(pkg_info_path)
        else:
            data = path_or_file.read(pkg_info_path)
        return cls.from_string(data.decode())

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
                if multiple:
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
            keywords="", home_page="", download_url="", author="",
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
        self.keywords = keywords
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


def _get_header_attributes(metadata_version):
    return HEADER_ATTRS.get(metadata_version, [])


def _parse(fp):
    return Parser().parse(fp)


def _must_decode(value):     #pragma NO COVER
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
        return '\n'.join([x[8:] if x.startswith(' ' * 8) else x
                          for x in txt.strip().splitlines()])
    else:
        return ' '.join([x.strip() for x in txt.splitlines()])
