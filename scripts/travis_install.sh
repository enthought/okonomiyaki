#! /bin/sh
set -e

pip install -U pip

if [ "${TRAVIS_PYTHON_VERSION}" == "2.6" ] || \
    [ "${TRAVIS_PYTHON_VERSION}" == "2.7" ] || \
    [ "${TRAVIS_PYTHON_VERSION}" == "pypy" ]; then
    pip install -rdev_requirements2.txt;
else
    pip install -rdev_requirements.txt;
fi

pip install .
