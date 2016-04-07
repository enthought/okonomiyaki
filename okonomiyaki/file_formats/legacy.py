""" Various functions to guess metadata for old eggs that did not define those
metadata.
"""
import re

from ..errors import InvalidMetadata, InvalidMetadataField


# To parse the python field in our index and spec/depend
_PYVER_RE = re.compile("(?P<major>\d+)\.(?P<minor>\d+)")

# To parse python_tag
_TAG_RE = re.compile("""
    (?P<interpreter>(cp|pp|cpython|py))
    (?P<version>([\d_]+))
""", flags=re.VERBOSE)


def _guess_abi_tag(epd_platform, python_tag):
    if python_tag is None:
        # No python tag, so should only be a "pure binary" egg, i.e.
        # an egg containing no python code and no python C extensions.
        return None

    if epd_platform is None:
        # No platform, so should only be a "pure python" egg, i.e.
        # an egg containing no C extension.
        return None

    # For legacy (aka legacy spec version info < 1.3), we know that pyver
    # can only be one of "2.X" with X in (5, 6, 7).
    #
    # In those cases, the mapping (platform pyver) -> ABI is unambiguous,
    # as we only ever used one ABI for a given python version/platform.
    pyver = _python_tag_to_python(python_tag)
    return "cp{0}{1}m".format(pyver[0], pyver[2])


def _guess_python_tag(major_minor):
    """ Compute the python_tag entry from the python value.  The returned value
    may be None.

    Parameters
    ----------
    major_minor : str or None
        The python version in M.N format (e.g. `2.7`)

    Note
    ----
    This should only be used for backward compatiblity reason
    """
    if major_minor in (None, ""):
        return None
    else:
        m = _PYVER_RE.search(major_minor)
        if m is None:
            msg = "python_tag cannot be guessed for python = {0}"
            raise InvalidMetadata(msg.format(major_minor))
        else:
            major = m.groupdict()["major"]
            minor = m.groupdict()["minor"]

            return "cp" + major + minor


def _python_tag_to_python(python_tag):
    # This converts only python version we currently intent to support in
    # metadata version 1.x.
    if python_tag is None:
        return None

    generic_exc = InvalidMetadataField('python_tag', python_tag)

    m = _TAG_RE.match(python_tag)
    if m is None:
        raise generic_exc
    else:
        d = m.groupdict()
        version = d["version"]
        if len(version) == 1:
            if version == "2":
                return "2.7"
            else:
                raise generic_exc
        elif len(version) == 2:
            return "{0}.{1}".format(version[0], version[1])
        else:
            raise generic_exc
