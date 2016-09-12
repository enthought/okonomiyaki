import os.path


DUMMY_RUNTIMES_DIRECTORY = _HERE = os.path.dirname(__file__)

# Dummy runtimes for testing

# 2.7.9
PYTHON_CPYTHON_2_7_9_RH5_X86_64 = os.path.join(
    _HERE, "cpython-2.7.9+1-rh5_x86_64-gnu.runtime",
)
PYTHON_CPYTHON_2_7_9_OSX_X86_64 = os.path.join(
    _HERE, "cpython-2.7.9+1-osx_x86_64-darwin.runtime"
)
PYTHON_CPYTHON_2_7_9_WIN_X86 = os.path.join(
    _HERE, "cpython-2.7.9+1-win_x86-msvc2008.runtime",
)
PYTHON_CPYTHON_2_7_9_WIN_X86_64 = os.path.join(
    _HERE, "cpython-2.7.9+1-win_x86_64-msvc2008.runtime",
)

# 2.7.10
PYTHON_CPYTHON_2_7_10_RH5_X86_64 = os.path.join(
    _HERE, "cpython-2.7.10+1-rh5_x86_64-gnu.runtime",
)
PYTHON_CPYTHON_2_7_10_OSX_X86_64 = os.path.join(
    _HERE, "cpython-2.7.10+1-osx_x86_64-darwin.runtime"
)
PYTHON_CPYTHON_2_7_10_WIN_X86 = os.path.join(
    _HERE, "cpython-2.7.10+1-win_x86-msvc2008.runtime",
)
PYTHON_CPYTHON_2_7_10_WIN_X86_64 = os.path.join(
    _HERE, "cpython-2.7.10+1-win_x86_64-msvc2008.runtime",
)

# 3.4.1
PYTHON_CPYTHON_3_4_1_RH5_X86_64 = os.path.join(
    _HERE, "cpython-3.4.1+1-rh5_x86_64-gnu.runtime",
)
PYTHON_CPYTHON_3_4_1_OSX_X86_64 = os.path.join(
    _HERE, "cpython-3.4.1+1-osx_x86_64-darwin.runtime",
)
PYTHON_CPYTHON_3_4_1_WIN_X86 = os.path.join(
    _HERE, "cpython-3.4.1+1-win_x86-msvc2008.runtime",
)
PYTHON_CPYTHON_3_4_1_WIN_X86_64 = os.path.join(
    _HERE, "cpython-3.4.1+1-win_x86_64-msvc2008.runtime",
)

# 3.5.1
PYTHON_CPYTHON_3_5_1_RH5_X86_64 = os.path.join(
    _HERE, "cpython-3.5.1+1-rh5_x86_64-gnu.runtime",
)
PYTHON_CPYTHON_3_5_1_OSX_X86_64 = os.path.join(
    _HERE, "cpython-3.5.1+1-osx_x86_64-darwin.runtime",
)
PYTHON_CPYTHON_3_5_1_WIN_X86 = os.path.join(
    _HERE, "cpython-3.5.1+1-win_x86-msvc2008.runtime",
)
PYTHON_CPYTHON_3_5_1_WIN_X86_64 = os.path.join(
    _HERE, "cpython-3.5.1+1-win_x86_64-msvc2008.runtime",
)

PYTHON_CPYTHON_2_7_10_RH5_X86_64_INVALID = os.path.join(
    _HERE, "cpython-2.7.10+1-rh5_x86_64-gnu.runtime.invalid",
)
PYTHON_PYPY_2_6_0_RH5_X86_64 = os.path.join(
    _HERE, "pypy-2.6.0+1-rh5_x86_64-gnu.runtime",
)
JULIA_DEFAULT_0_3_11_RH5_X86_64 = os.path.join(
    _HERE, "julia-0.3.11+1-rh5_x86_64-gnu.runtime",
)
JULIA_DEFAULT_0_3_11_WIN_X86_64 = os.path.join(
    _HERE, "julia-0.3.11+1-win_x86_64-mingw.runtime",
)
R_DEFAULT_3_0_0_RH5_X86_64 = os.path.join(
    _HERE, "r-3.0.0+1-rh5_x86_64-gnu.runtime",
)

# Invalid runtimes
INVALID_RUNTIME_NO_METADATA_VERSION = os.path.join(
    _HERE, "cpython-2.7.9+2-rh5_x86_64-gnu.runtime.invalid",
)

# Dummmy eggs for testing
_RH5_X86_64 = os.path.join(_HERE, "eggs", "rh5_x86_64")

NOSE_1_3_4_RH5_X86_64 = os.path.join(_RH5_X86_64, "nose-1.3.4-1.egg")
MKL_10_3_RH5_X86_64 = os.path.join(_RH5_X86_64, "MKL-10.3-1.egg")
NUMPY_1_9_2_RH5_X86_64 = os.path.join(_RH5_X86_64, "numpy-1.9.2-1.egg")

_WIN_X86_64 = os.path.join(_HERE, "eggs", "rh5_x86_64")

NOSE_1_3_4_WIN_X86_64 = os.path.join(_WIN_X86_64, "nose-1.3.4-1.egg")
MKL_10_3_WIN_X86_64 = os.path.join(_WIN_X86_64, "MKL-10.3-1.egg")
NUMPY_1_9_2_WIN_X86_64 = os.path.join(_WIN_X86_64, "numpy-1.9.2-1.egg")

_OSX_X86_64 = os.path.join(_HERE, "eggs", "rh5_x86_64")

NOSE_1_3_4_OSX_X86_64 = os.path.join(_OSX_X86_64, "nose-1.3.4-1.egg")
MKL_10_3_OSX_X86_64 = os.path.join(_OSX_X86_64, "MKL-10.3-1.egg")
NUMPY_1_9_2_OSX_X86_64 = os.path.join(_OSX_X86_64, "numpy-1.9.2-1.egg")
