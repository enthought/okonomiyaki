import sys
import unittest
import re
from unittest import mock

from packaging import tags

from .. import _pep425_impl
from ..pep425 import compute_abi_tag, compute_python_tag, compute_platform_tag


def _system_tags():
    interp_name = tags.interpreter_name()
    if interp_name == "cp":
        for tag in tags.cpython_tags():
            yield tag
    else:
        for tag in tags.generic_tags():
            yield tag


class TestPEP425(unittest.TestCase):

    def setUp(self):
        self.tag = next(
            tag for tag in
            _system_tags()
            # We do not support the manylinux tag
            if 'manylinux' not in tag.platform)
        self.compatible_platforms = tuple(
            tag.platform for tag in _system_tags())

    def test_abi_tag(self):
        # Given
        executable = sys.executable

        # When
        abi_tag = compute_abi_tag(executable)

        # Then
        self.assertEqual(abi_tag, self.tag.abi)

    def test_abi_tag_default(self):
        # When
        abi_tag = compute_abi_tag()

        # Then
        self.assertEqual(abi_tag, self.tag.abi)

    def test_python_tag(self):
        # Given
        executable = sys.executable

        # When
        python_tag = compute_python_tag(executable)

        # Then
        self.assertEqual(python_tag, self.tag.interpreter)

    def test_python_tag_default(self):
        # When
        python_tag = compute_python_tag()

        # Then
        self.assertEqual(python_tag, self.tag.interpreter)

    def test_platform_tag(self):
        # Given
        executable = sys.executable

        # When
        platform_tag = compute_platform_tag(executable)

        # Then
        if sys.platform.startswith('darwin'):
            # packaging always sets the minor macos version to 0
            platform_tag = re.sub('macosx_11_.', 'macosx_11_0', platform_tag)
            platform_tag = re.sub('macosx_12_.', 'macosx_12_0', platform_tag)
        else:
            self.assertIn(platform_tag, self.compatible_platforms)

    def test_platform_tag_default(self):
        # When
        platform_tag = compute_platform_tag()

        # Then
        # Then
        if sys.platform.startswith('darwin'):
            # packaging always sets the minor macos version to 0
            platform_tag = re.sub('macosx_11_.', 'macosx_11_0', platform_tag)
            platform_tag = re.sub('macosx_12_.', 'macosx_12_0', platform_tag)
        else:
            self.assertIn(platform_tag, self.compatible_platforms)


class TestGetAbiTagFreeThreaded(unittest.TestCase):
    """ get_abi_tag() emulates CPython's abi tag directly rather than
    running on an actual free-threaded interpreter, so exercise it against
    a simulated free-threaded config var instead of relying on CI having a
    free-threaded build available.
    """

    def _get_abi_tag(self, config_vars, version_info):
        namespace = {}
        exec(
            compile(_pep425_impl._PEP425_IMPL, "<pep425_impl>", "exec"),
            namespace,
        )
        with mock.patch.object(
            namespace["sysconfig"], "get_config_var",
            side_effect=config_vars.get,
        ), mock.patch.object(
            namespace["sys"], "version_info", version_info,
        ):
            return namespace["get_abi_tag"]()

    def test_free_threaded_cpython_includes_t_flag(self):
        abi_tag = self._get_abi_tag(
            {"Py_GIL_DISABLED": True}, (3, 14, 0, "final", 0))
        self.assertEqual(abi_tag, "cp314t")

    def test_non_free_threaded_cpython_has_no_t_flag(self):
        abi_tag = self._get_abi_tag(
            {"Py_GIL_DISABLED": False}, (3, 14, 0, "final", 0))
        self.assertEqual(abi_tag, "cp314")

    def test_free_threaded_flag_ignored_before_py313(self):
        # Py_GIL_DISABLED does not exist before 3.13; a truthy value there
        # should not be trusted.
        abi_tag = self._get_abi_tag(
            {"Py_GIL_DISABLED": True}, (3, 12, 0, "final", 0))
        self.assertEqual(abi_tag, "cp312")
