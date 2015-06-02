# flake8: noqa
from .epd_platform import EPDPlatform, applies
from .platform import Platform
from ._arch import X86, X86_64

__all__ = ["EPDPlatform", "Platform"]
__all__.extend([X86, X86_64])
