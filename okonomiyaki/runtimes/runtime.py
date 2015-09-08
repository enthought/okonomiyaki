import ntpath
import posixpath
import sys

import six

from attr import attr, attributes
from attr.validators import instance_of

from okonomiyaki.platforms import Platform
from okonomiyaki.platforms.platform import WINDOWS
from okonomiyaki.runtimes import RuntimeVersion
from okonomiyaki.versions import MetadataVersion

from .runtime_info import IRuntimeInfoV1, PythonRuntimeInfoV1


# Those *Runtime classes are not very useful at the moment, and don't really
# belong in okonomiyaki. We need them here as they are required for enstaller,
# but will be removed once jaguar and enstaller are merged together.
@attributes
class Runtime(object):
    """ Runtime instances are used to manipulate installed runtimes.
    """
    _runtime_info = attr(validator=instance_of(IRuntimeInfoV1))

    @property
    def executable(self):
        "The full path to the runtime interpreter."
        return self._metadata_klass.executable

    @property
    def prefix(self):
        "The full path prefix to this runtime."
        return self._runtime_info.prefix


@attributes
class PythonRuntime(Runtime):
    """ A runtime with python-specific attributes.

    It also implements some functionality for enstaller legacy support.
    """
    _executable = attr(validator=instance_of(six.text_type))

    @classmethod
    def from_prefix_and_platform(cls, prefix, platform, version):
        """ Use this to build a runtime for an arbitrary platform.

        Calling this with an incompatible platform (e.g. windows on linux) is
        undefined.

        Parameters
        ----------
        prefix: text
            An absolute path to the prefix (the root of the runtime), e.g. for
            a standard unix python, if python is in <prefix>/bin/python,
            <prefix> is the prefix.
        platform: Platform
            An okonomiyaki Platform class (the vendorized one).
        version: SemanticVersion
            The runtime's version
        """
        if platform.os == WINDOWS:
            prefix = ntpath.normpath(prefix)
            scriptsdir = ntpath.join(prefix, "Scripts")
            paths = (prefix, scriptsdir)
        else:
            prefix = posixpath.normpath(prefix)
            scriptsdir = bindir = posixpath.join(prefix, "bin")
            paths = (bindir, )

        if version.major == 3:
            executable = u"python3"
        else:
            executable = u"python2"

        major_minor = "{0}.{1}".format(version.major, version.minor)

        if platform.os == WINDOWS:
            executable += ".exe"
            executable = ntpath.join(prefix, executable)
        else:
            executable = posixpath.join(scriptsdir, executable)

        site_packages = _compute_site_packages(prefix, platform, major_minor)

        language = u"python"
        implementation = u"cpython"
        build_revision = u""
        name = u"<dummy>"
        post_install = tuple()

        runtime_info = PythonRuntimeInfoV1(
            MetadataVersion.from_string("1.0"), language, implementation,
            version, platform, build_revision, executable, paths, post_install,
            prefix, name, scriptsdir, site_packages,

        )
        return cls(runtime_info, u"")

    @classmethod
    def from_running_python(cls, platform=None):
        """ Use this to compute runtime info from the running python.

        Calling this with an incompatible platform (e.g. windows on linux) is
        undefined.

        Parameters
        ----------
        platform: Platform
            An okonomiyaki Platform class (the vendorized one).
        """
        if six.PY2:
            prefix = sys.exec_prefix.decode(sys.getfilesystemencoding())
        else:
            prefix = sys.exec_prefix

        platform = platform or Platform.from_running_python()
        version = _version_info_to_version()

        return cls.from_prefix_and_platform(prefix, platform, version)

    @property
    def executable(self):
        "The full path to the python binary."
        if len(self._executable) == 0:
            self._executable = self._compute_executable()
        return self._executable

    @property
    def scriptsdir(self):
        """The full path to the scripts directory, i.e. the directory where
        setuptools entry points are usually placed.
        """
        return self._runtime_info.scriptsdir

    @property
    def site_packages(self):
        """The full path to this runtime site-packages.
        """
        return self._runtime_info.site_packages

    def _compute_executable(self):
        if self._runtime_info.platform.os == WINDOWS:
            # Hack to take into account virtualenvs
            paths = (
                self._runtime_info.executable,
                ntpath.join(
                    self.scriptsdir, ntpath.basename(self._executable_value)
                )
            )
            for path in paths:
                if ntpath.isfile(path):
                    return path
            return self._runtime_info.executable
        else:
            return self._runtime_info.executable


def _compute_site_packages(prefix, platform, major_minor):
    # Adapted from distutils.sysconfig.get_python_lib for 2.7.9
    prefix = prefix or sys.exec_prefix

    if platform.os == WINDOWS:
        return ntpath.join(prefix, "Lib", "site-packages")
    else:
        return posixpath.join(
            prefix, "lib", "python" + major_minor, "site-packages"
        )


def _version_info_to_version(version_info=None):
    version_info = version_info or sys.version_info
    version_string = ".".join(str(part) for part in version_info[:3])
    version_string += "-{0}.{1}".format(*version_info[-2:])
    return RuntimeVersion.from_string(version_string)