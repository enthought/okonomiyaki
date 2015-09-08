import os.path


_HERE = os.path.dirname(__file__)

# Dummy runtimes for testing
PYTHON_CPYTHON_2_7_10_RH5_64 = os.path.join(
    _HERE, "python-cpython-2.7.10-1-rh5_x86_64.runtime",
)
PYTHON_CPYTHON_2_7_10_WIN_64 = os.path.join(
    _HERE, "python-cpython-2.7.10-1-win_x86_64.runtime",
)
PYTHON_CPYTHON_2_7_10_RH5_64_INVALID = os.path.join(
    _HERE, "python-cpython-2.7.10-1-rh5_x86_64.runtime.invalid",
)
JULIA_DEFAULT_0_3_11_RH5_64 = os.path.join(
    _HERE, "julia-default-0.3.11-1-rh5_x86_64.runtime",
)
JULIA_DEFAULT_0_3_11_WIN_64 = os.path.join(
    _HERE, "julia-default-0.3.11-1-win_x86_64.runtime",
)
R_DEFAULT_3_0_0_RH5_64 = os.path.join(
    _HERE, "r-default-3.0.0-1-rh5_x86_64.runtime",
)