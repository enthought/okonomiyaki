from __future__ import absolute_import

#  Copyright (c) 2013 by Enthought, Inc.
#  All rights reserved.
try:
    from ._version import (
        version as __version__, version_info as __version_info__
    )
except ImportError:
    __version__ = "unknown"
    __version_info__ = (0, 0, 0, "unknown", 0)
