#! /bin/sh
set -e

if [ "${TRAVIS_PYTHON_VERSION}" == "2.6" ] || [ "${TRAVIS_PYTHON_VERSION}" == "2.7" ]; then
    pip install -rdev_requirements2.txt;
elif [[ "${TRAVIS_PYTHON_VERSION}" = "3.4" ]]; then
    deactivate;
    python3.4 -m venv ~/virtualenv/python3.4;
    source ~/virtualenv/python3.4/bin/activate;
    python -m ensurepip;
    python -m pip install -r dev_requirements.txt;
else
    pip install -rdev_requirements.txt;
fi

pip install .
