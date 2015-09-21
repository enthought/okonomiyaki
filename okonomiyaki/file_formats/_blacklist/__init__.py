from __future__ import absolute_import

import os.path

from .pkg_info_data import (
    EGG_PKG_INFO_BLACK_LIST, may_be_in_pkg_info_blacklist
)
from .python_tag import (
    EGG_PYTHON_TAG_BLACK_LIST, may_be_in_python_tag_blacklist
)


_EGG_PLATFORM_BLACK_LIST = {
    "7z-9.20-1.egg": {
        "0c288adacaa1f4e3aa7a32cbd8fb72b1e33277e147b9326f9c7487f69971d62d":
            "win-64",
        "d5c942864c78593c23808d7445bd634eeedff869fbb891382bdc8e6b44782115":
            "win-32",
    },
    "cmake-3.0.2-1.egg": {
        "9bbe16ce22a5a6c10c270ebff4ce9e3aeef50c0378fcd9a2f6d20a57b1920605":
            "win-64",
        "647bd9ac546629915587c2ee2fcf485f0478b043692be15a9ee81ef2a10bed3e":
            "win-32",
    },
    "cmake-3.0.2-2.egg": {
        "f4208b3c6b6015e26b280461e4130ce8d9bb866e9aa1d2983e619131156d4c00":
            "win-64",
        "599912425058027e9b968a5ff343c278dc5ff00b59e96a4006ba867ca8683a45":
            "win-32",
    },
    "cmake-3.1.1-1.egg": {
        "f2cc7562a16cba76c2dddcb5ea9a19376ac32f4a28b5a96d1688c632252d8bbc":
            "win-64",
        "7b89c3b6d2878ff3be36131525a9bb616c4f54c6d71d9125cd3612a6fd403c9f":
            "win-32",
    },
    "_registry_path-1.0-2.egg": {
        "9f040cbe901c0f827e5993a8476e768c40a399d69edde567610d59a3848530aa":
            "win-64",
        "21e03dd728f91b4bd59ad80e73ada7d5c5cea6acf2a7f7e3d25a92ba9992f07c":
            "win-32",
    },
    "swig-2.0.12-1.egg": {
        "61c7e809010cb84b5c7f9a372c4e013b0ab0c0e7e5831a29f885429918849878":
            "win-32",
        "9284aca09bced708bd3636544a8fc6ea2d4e6fe8fca07f25fbea0fd5f17c424a":
            "win-64",
    },
    "swig-3.0.2-1.egg": {
        "c2aae31db93fac0b9d6987895ce817d0320dad168b3fbe296f0bc923cad7a42b":
            "win-32",
        "0991cf20ea41f5da52e2b973bdf199b85c08eaba7d5fef0bf782ae776da386d6":
            "win-64",
    },
    "tar-1.13-1.egg": {
        "4cd5870a3d003b32b55867b96321985adac3a6145ea9a4f8c8780558f8780e21":
            "win-64",
        "0f75d5c927087dc89aa0afaecd489457c9f40ea51bec595fcc5bbb8a9b3fff5b":
            "win-32"
    },
    "xz-5.2.0-1.egg": {
        "ca5f2c417dd9f6354db3c2999edb441382ed11c7a034ade1839d1871a78ab2e8":
            "win-32",
        "a5b473426764ed83faaf9366381022f3c2a087d098ccb9873ae8826673cc4f84":
            "win-64",
    },
}


# (egg sha256) -> (epd platform string) mapping
EGG_PLATFORM_BLACK_LIST = dict(
    (checksum, platform_string)
    for egg in _EGG_PLATFORM_BLACK_LIST.values()
    for checksum, platform_string in egg.items()
)


def may_be_in_platform_blacklist(path):
    """ Returns True if the given egg path may be in the PKG INFO blacklist.
    """
    return os.path.basename(path) in _EGG_PLATFORM_BLACK_LIST


__all__ = [
    "CONTENT_SPEC_DEPEND_PLATFORM_BLACK_LIST", "EGG_PKG_INFO_BLACK_LIST",
    "EGG_PYTHON_TAG_BLACK_LIST", "may_be_in_pkg_info_blacklist",
    "may_be_in_python_tag_blacklist", "may_be_in_platform_blacklist",
]
