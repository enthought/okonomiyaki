from __future__ import absolute_import

from .pkg_info_data import EGG_PKG_INFO_BLACK_LIST


# egg sha256 to epd platform string
EGG_PLATFORM_BLACK_LIST = {
    "9284aca09bced708bd3636544a8fc6ea2d4e6fe8fca07f25fbea0fd5f17c424a":
        "win-64",
    "0991cf20ea41f5da52e2b973bdf199b85c08eaba7d5fef0bf782ae776da386d6":
        "win-64",
    "a5b473426764ed83faaf9366381022f3c2a087d098ccb9873ae8826673cc4f84":
        "win-64",
    "61c7e809010cb84b5c7f9a372c4e013b0ab0c0e7e5831a29f885429918849878":
        "win-32",
    "c2aae31db93fac0b9d6987895ce817d0320dad168b3fbe296f0bc923cad7a42b":
        "win-32",
    "ca5f2c417dd9f6354db3c2999edb441382ed11c7a034ade1839d1871a78ab2e8":
        "win-32",

}

__all__ = [
    "CONTENT_SPEC_DEPEND_PLATFORM_BLACK_LIST",
    "EGG_PKG_INFO_BLACK_LIST"
]
