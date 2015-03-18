# flake8: noqa
from .epd_platform import EPDPlatform, applies
from .platform import Platform

# Other variables above will hopefully disappear before v1
__all__ = ["EPDPlatform", "Platform"]
