import os.path

from attr import attributes, attr
from attr.validators import instance_of

from okonomiyaki.errors import OkonomiyakiError
from ._wheel_common import _R_WHEEL_BASE


@attributes
class WheelInfo(object):
    name = attr()
    version = attr()
    python_tags = attr(validator=instance_of(tuple))
    python_abi_tags = attr(validator=instance_of(tuple))
    platforms = attr(validator=instance_of(tuple))

    build = attr(default=None)

    @classmethod
    def from_path(cls, path):
        basename = os.path.basename(path)
        m = _R_WHEEL_BASE.match(basename)
        if m is None:
            raise OkonomiyakiError(
                u"Unrecognized filename format '{0}'".format(path)
            )

        name = m.group("name")
        version = m.group("ver")

        python_tag_strings = tuple(m.group("pyver").split("."))
        python_abi_strings = tuple(m.group("abi").split("."))
        platforms = tuple(m.group("plat").split("."))

        build = m.group("build")

        return cls(
            name, version, python_tag_strings, python_abi_strings, platforms,
            build
        )
