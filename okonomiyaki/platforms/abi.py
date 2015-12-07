from ..errors import OkonomiyakiError
from ..versions import RuntimeVersion

from .epd_platform import EPDPlatform
from .platform import DARWIN, LINUX, WINDOWS


def _default_cpython_abi(platform, implementation_version):
    msg = (
        "Unsupported platform/version combo for cpython: {0!r}/{1!r}".
        format(platform, implementation_version)
    )

    if platform.os == DARWIN:
        return u"darwin"
    elif platform.os == LINUX:
        return u"gnu"
    elif platform.os == WINDOWS:
        abi = None
        if implementation_version.major == 2:
            abi = u"msvc2008"
        elif implementation_version.major == 3:
            if implementation_version.minor <= 4:
                abi = u"msvc2010"
            elif implementation_version.minor == 5:
                abi = u"msvc2015"

        if abi is None:
            raise OkonomiyakiError(msg)

        return abi
    else:
        raise OkonomiyakiError(msg)


def default_abi(platform, implementation, implementation_version):
    """ Returns the default abi for the given platform and python
    implementation.

    Parameters
    ----------
    platform : Platform or str
        The platform to get the default abi for
    implementation: str
        The language implementation (e.g. 'cpython', 'julia')
    implementation_version : RuntimeVersion or str
        The runtime version.

    Note
    ----
    For arguments accepting both object and str arguments, the str is
    automatically converted into an instance of the corresponding class.
    """
    if isinstance(platform, str):
        platform = EPDPlatform.from_epd_string(platform).platform
    if isinstance(implementation_version, str):
        implementation_version = RuntimeVersion.from_string(
            implementation_version
        )

    msg = "Unsupported platform/version combo for {0!r}: {1!r}/{2!r}".format(
        implementation, platform, str(implementation_version)
    )

    if implementation == "cpython":
        return _default_cpython_abi(platform, implementation_version)
    elif implementation == "pypy":
        if platform.os == WINDOWS:
            if implementation_version <= RuntimeVersion.from_string("4.1"):
                return u"msvc2008"
            else:
                raise OkonomiyakiError(msg)
        elif platform.os == LINUX:
            return u"gnu"
        elif platform.os == DARWIN:
            return u"darwin"
        else:
            raise OkonomiyakiError(msg)
    elif implementation == "julia":
        if platform.os == WINDOWS:
            return u"mingw"
        elif platform.os == LINUX:
            return u"gnu"
        elif platform.os == DARWIN:
            return u"darwin"
        else:
            raise OkonomiyakiError(msg)
    else:
        raise OkonomiyakiError(
            "Unsupported implementation: {0!r}".format(implementation)
        )
