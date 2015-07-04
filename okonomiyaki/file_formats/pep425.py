import re

from ..errors import InvalidMetadata


_KIND_TO_ABBREVIATED = {
    "cpython": "cp",
    "python": "py",
    "pypy": "pp",
}

_ABBREVIATED_TO_KIND = dict((v, k) for k, v in _KIND_TO_ABBREVIATED.items())

_TAG_RE = re.compile("""
    (?P<interpreter>([^\d]+))
    (?P<version>([\d_]+))
""", flags=re.VERBOSE)


class PythonImplementation(object):
    @classmethod
    def from_string(cls, s):
        m = _TAG_RE.match(s)
        if m is None:
            msg = "Invalid python tag string: {!r}".format(s)
            raise InvalidMetadata(msg)
        else:
            d = m.groupdict()
            kind = d["interpreter"]
            version = d["version"]
            if len(version) < 2:
                msg = "Compressed python cannot be converted"
                raise InvalidMetadata(msg)
            elif len(version) > 2:
                msg = "Python tag {0!r} not understood"
                raise InvalidMetadata(msg.format(version))
            else:
                major = int(version[0])
                minor = int(version[1])
                return cls(kind, major, minor)

    def __init__(self, kind, major, minor):
        self.kind = _ABBREVIATED_TO_KIND.get(kind, kind)
        self.major = major
        self.minor = minor

    @property
    def abbreviated_implementation(self):
        return _KIND_TO_ABBREVIATED.get(self.kind, self.kind)

    @property
    def pep425_tag(self):
        """ PEP425-compliant python tag string. """
        return str(self)

    def __str__(self):
        return "{0.abbreviated_implementation}{0.major}{0.minor}".format(self)
