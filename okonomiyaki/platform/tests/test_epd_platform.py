import unittest

from okonomiyaki.platform import EPD_PLATFORM_SHORT_NAMES, EPDPlatform
from okonomiyaki.platform.legacy import _SUBDIR

class TestEPDPlatform(unittest.TestCase):
    def test_short_names_consistency(self):
        legacy_entries = sorted([entry[0] for entry in _SUBDIR])

        self.assertEqual(EPD_PLATFORM_SHORT_NAMES, legacy_entries)

    def test_epd_platform_from_string(self):
        """Ensure every epd short platform is understood by EPDPlatform."""
        for epd_platform_string in EPD_PLATFORM_SHORT_NAMES:
            EPDPlatform.from_epd_string(epd_platform_string)
