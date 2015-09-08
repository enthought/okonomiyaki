import os.path
import sys
import unittest

from okonomiyaki.platforms import EPDPlatform
from okonomiyaki.runtimes import RuntimeVersion

from ..runtime import PythonRuntime


NORM_EXEC_PREFIX = os.path.normpath(sys.exec_prefix)
NORM_EXECUTABLE = os.path.normpath(sys.executable)
if sys.version_info[0] == 2:
    NORM_EXEC_PREFIX = NORM_EXEC_PREFIX.decode(sys.getfilesystemencoding())
    NORM_EXECUTABLE = NORM_EXECUTABLE.decode(sys.getfilesystemencoding())


class TestPythonRuntime(unittest.TestCase):
    def test_simple_from_running_python(self):
        # When
        runtime_info = PythonRuntime.from_running_python()

        # Then
        self.assertEqual(runtime_info.prefix, NORM_EXEC_PREFIX)
        self.assertEqual(
            os.path.realpath(runtime_info.executable),
            os.path.realpath(NORM_EXECUTABLE)
        )

    def test_from_prefix_and_platform(self):
        # Given
        prefix = u"/usr/local"
        platform = EPDPlatform.from_epd_string("rh5-64").platform
        version = RuntimeVersion.from_string("3.4.3-final.0")

        # When
        runtime_info = PythonRuntime.from_prefix_and_platform(
            prefix, platform, version
        )

        # Then
        self.assertEqual(runtime_info.executable, prefix + "/bin/python3")
        self.assertEqual(runtime_info.prefix, prefix)
        self.assertEqual(runtime_info.scriptsdir, prefix + "/bin")
        self.assertEqual(
            runtime_info.site_packages,
            prefix + "/lib/python3.4/site-packages")

        # Given
        prefix = u"/usr/local"
        platform = EPDPlatform.from_epd_string("osx-64").platform
        version = RuntimeVersion.from_string("2.7.9-final.0")

        # When
        runtime_info = PythonRuntime.from_prefix_and_platform(
            prefix, platform, version
        )

        # Then
        self.assertEqual(runtime_info.prefix, prefix)
        self.assertEqual(runtime_info.scriptsdir, prefix + "/bin")
        self.assertEqual(
            runtime_info.site_packages,
            prefix + "/lib/python2.7/site-packages")

        # Given
        prefix = u"C:\\Python34"
        platform = EPDPlatform.from_epd_string("win-64").platform
        version = RuntimeVersion.from_string("3.4.3-final.0")

        # When
        runtime_info = PythonRuntime.from_prefix_and_platform(
            prefix, platform, version
        )

        # Then
        self.assertEqual(runtime_info.prefix, prefix)
        self.assertEqual(runtime_info.scriptsdir, prefix + "\\Scripts")
        self.assertEqual(
            runtime_info.site_packages, prefix + "\\Lib\\site-packages")

    def test_normalization(self):
        # Given
        prefix = u"/usr/local/bin/.."
        norm_prefix = u"/usr/local"
        platform = EPDPlatform.from_epd_string("osx-64").platform
        version = RuntimeVersion.from_string("2.7.9-final.0")

        # When
        runtime_info = PythonRuntime.from_prefix_and_platform(
            prefix, platform, version
        )

        # Then
        self.assertEqual(runtime_info.prefix, norm_prefix)
        self.assertEqual(runtime_info.scriptsdir, norm_prefix + "/bin")
        self.assertEqual(
            runtime_info.site_packages,
            norm_prefix + "/lib/python2.7/site-packages")