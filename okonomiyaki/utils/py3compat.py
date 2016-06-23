import sys

import six


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


if PY2:
    def exec_(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")

    long = long
    string_types = basestring,

    binary_type = str
    text_type = unicode

    def u(s):
        return unicode(s.replace(r'\\', r'\\\\'), "unicode_escape")

    def iterkeys(d, **kw):
        return iter(d.iterkeys(**kw))

    def itervalues(d, **kw):
        return iter(d.itervalues(**kw))

    def iteritems(d, **kw):
        return iter(d.iteritems(**kw))

    import StringIO
    StringIO = BytesIO = StringIO.StringIO

else:
    import builtins
    exec_ = getattr(builtins, "exec")

    long = int
    string_types = str,

    binary_type = bytes
    text_type = str

    def u(s):
        return s

    def iterkeys(d, **kw):
        return iter(d.keys(**kw))

    def itervalues(d, **kw):
        return iter(d.values(**kw))

    def iteritems(d, **kw):
        return iter(d.items(**kw))

    import io
    StringIO = io.StringIO


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


def decode_if_needed(value):
    if isinstance(value, six.binary_type):
        return value.decode("utf8")
    return value


def encode_if_needed(value):
    if isinstance(value, six.text_type):
        return value.encode("utf8")
    return value
