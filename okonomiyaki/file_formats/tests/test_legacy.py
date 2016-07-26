import sys

if sys.version_info < (2, 7):  # noqa
    import unittest2 as unittest
else:
    import unittest

from okonomiyaki.platforms import EPDPlatform

from ..legacy import _guess_platform_abi


class TestGuessPlatformABI(unittest.TestCase):
    def test_brood_cases(self):
        # set of (python_tag, platform string) pairs that have at least one
        # index in our current instance of packages.e.com. This was computed
        # from a dump of our prod database w/ the following SQL:
        #
        # SELECT DISTINCT(python_tags.name, platforms.name, platforms.arch)
        # FROM egg_indices, python_tags, platforms
        # WHERE
        #   egg_indices.python_tag_id = python_tags.id
        #   and egg_indices.platform_id = platforms.id
        #
        # and
        #
        # SELECT DISTINCT(python_tags.name, platforms.name, platforms.arch)
        # FROM eggs, python_tags, platforms
        # WHERE
        #   eggs.python_tag_id = python_tags.id
        #   and eggs.platform_id = platforms.id
        #
        tag_platform = {
            ('cp27', 'osx_x86'): 'darwin',
            ('cp27', 'osx_x86_64'): 'darwin',
            ('cp27', 'rh5_x86'): 'gnu',
            ('cp27', 'rh5_x86_64'): 'gnu',
            ('cp27', 'win_x86'): 'msvc2008',
            ('cp27', 'win_x86_64'): 'msvc2008',
            ('cp30', 'osx_x86'): 'darwin',
            ('cp30', 'osx_x86_64'): 'darwin',
            ('cp30', 'rh5_x86'): 'gnu',
            ('cp30', 'rh5_x86_64'): 'gnu',
            ('cp30', 'win_x86'): 'msvc2008',
            ('cp30', 'win_x86_64'): 'msvc2008',
            ('cp31', 'osx_x86'): 'darwin',
            ('cp31', 'osx_x86_64'): 'darwin',
            ('cp31', 'rh5_x86'): 'gnu',
            ('cp31', 'rh5_x86_64'): 'gnu',
            ('cp31', 'win_x86'): 'msvc2008',
            ('cp31', 'win_x86_64'): 'msvc2008',
            ('cp32', 'osx_x86'): 'darwin',
            ('cp32', 'osx_x86_64'): 'darwin',
            ('cp32', 'rh5_x86'): 'gnu',
            ('cp32', 'rh5_x86_64'): 'gnu',
            ('cp32', 'win_x86'): 'msvc2008',
            ('cp32', 'win_x86_64'): 'msvc2008',
            ('cp33', 'osx_x86'): 'darwin',
            ('cp33', 'osx_x86_64'): 'darwin',
            ('cp33', 'rh5_x86'): 'gnu',
            ('cp33', 'rh5_x86_64'): 'gnu',
            ('cp33', 'win_x86'): 'msvc2010',
            ('cp33', 'win_x86_64'): 'msvc2010',
            ('cp34', 'osx_x86'): 'darwin',
            ('cp34', 'osx_x86_64'): 'darwin',
            ('cp34', 'rh5_x86'): 'gnu',
            ('cp34', 'rh5_x86_64'): 'gnu',
            ('cp34', 'win_x86'): 'msvc2010',
            ('cp34', 'win_x86_64'): 'msvc2010',
            ('ip27', 'osx_x86'): 'darwin',
            ('ip27', 'osx_x86_64'): 'darwin',
            ('ip27', 'rh5_x86'): 'gnu',
            ('ip27', 'rh5_x86_64'): 'gnu',
            ('ip27', 'win_x86'): 'msvc2008',
            ('ip27', 'win_x86_64'): 'msvc2008',
            ('jy27', 'osx_x86'): 'darwin',
            ('jy27', 'osx_x86_64'): 'darwin',
            ('jy27', 'rh5_x86'): 'gnu',
            ('jy27', 'rh5_x86_64'): 'gnu',
            ('jy27', 'win_x86'): 'msvc2008',
            ('jy27', 'win_x86_64'): 'msvc2008',
            ('pp27', 'osx_x86'): 'darwin',
            ('pp27', 'osx_x86_64'): 'darwin',
            ('pp27', 'rh5_x86'): 'gnu',
            ('pp27', 'rh5_x86_64'): 'gnu',
            ('pp27', 'win_x86'): 'msvc2008',
            ('pp27', 'win_x86_64'): 'msvc2008',
        }
        for (python_tag, epd_string), platform_abi in tag_platform.items():
            epd_platform = EPDPlatform.from_string(epd_string)
            self.assertEqual(
                _guess_platform_abi(epd_platform, python_tag), platform_abi
            )
