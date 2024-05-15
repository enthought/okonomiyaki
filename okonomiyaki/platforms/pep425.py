import os
import subprocess
import sys
import tempfile


from okonomiyaki.utils import decode_if_needed
from ._pep425_impl import _PEP425_IMPL
from ._platform import OSKind
from ._arch import X86, X86_64, ARM, ARM64

_ANY_PLATFORM_STRING = 'any'
_MACHINE2TEMPLATE = {
    (OSKind.darwin, X86): 'macosx_{}_i386',
    (OSKind.darwin, X86_64): 'macosx_{}_x86_64',
    (OSKind.darwin, ARM64): 'macosx_{}_arm64',
    (OSKind.linux, X86): 'linux_i686',
    (OSKind.linux, X86_64): 'linux_x86_64',
    (OSKind.linux, ARM): 'linux_aarch32',
    (OSKind.linux, ARM64): 'linux_aarch64',
    (OSKind.windows, X86): 'win32',
    (OSKind.windows, X86_64): 'win_amd64',
    (OSKind.windows, ARM64): 'win_arm64',
}


def _run_pep425(executable, flag):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as handle:
        handle.write(_PEP425_IMPL)
    try:
        out = subprocess.check_output([executable, handle.name, flag]).strip()
    finally:
        os.remove(handle.name)
    return decode_if_needed(out)


def compute_abi_tag(python_executable=None):
    """ Compute the PEP425 abi tag for the given python executable.

    This will launch a subprocess.
    """
    if python_executable is None:
        python_executable = sys.executable
    return _run_pep425(python_executable, "--abi-tag")


def compute_python_tag(python_executable=None):
    """ Compute the PEP425 python tag for the given python executable.

    This will launch a subprocess.
    """
    if python_executable is None:
        python_executable = sys.executable
    return _run_pep425(python_executable, "--python-tag")


def compute_platform_tag(python_executable=None):
    """ Compute the PEP425 platform tag for the given python executable.

    This will launch a subprocess.
    """
    if python_executable is None:
        python_executable = sys.executable
    return _run_pep425(python_executable, "--platform-tag")


def generate_platform_tag(platform, as_string=False):
    """ Generate a platform tag from a Platform instance

    """
    if platform is None:
        return _ANY_PLATFORM_STRING if as_string else None
    machine = platform.os_kind, platform.arch
    try:
        tag = _MACHINE2TEMPLATE[machine]
    except KeyError:
        msg = "Cannot generate pep425 tag for platform {0!r}"
        raise OkonomiyakiError(msg.format(platform))
    if platform.os_kind == OSKind.darwin:
        release = platform.release.replace('.', '_')
        return tag.format(release)
    else:
        return tag
