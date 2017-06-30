import subprocess


from okonomiyaki.utils import decode_if_needed
from . import _pep425_impl


_PEP425_IMPL = _pep425_impl.__file__


def _run_pep425(executable, flag):
    out = subprocess.check_output([executable, _PEP425_IMPL, flag]).strip()
    return decode_if_needed(out)


def compute_abi_tag(python_executable=None):
    """ Compute the PEP425 abi tag for the given python executable.

    This may launch a subprocess if python_executable is not the running python
    """
    if python_executable is None:
        return _pep425_impl.get_abi_tag()
    else:
        return _run_pep425(python_executable, "--abi-tag")


def compute_python_tag(python_executable=None):
    """ Compute the PEP425 python tag for the given python executable.

    This may launch a subprocess if python_executable is not the running python
    """
    if python_executable is None:
        return _pep425_impl.get_impl_tag()
    else:
        return _run_pep425(python_executable, "--python-tag")


def compute_platform_tag(python_executable=None):
    """ Compute the PEP425 platform tag for the given python executable.

    This may launch a subprocess if python_executable is not the running python
    """
    if python_executable is None:
        return _pep425_impl.get_platform()
    else:
        return _run_pep425(python_executable, "--platform-tag")
