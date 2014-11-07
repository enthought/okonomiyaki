#! /bin/sh
set -e

if [ "${TRAVIS_PYTHON_VERSION}" == "2.6" ] || [ "${TRAVIS_PYTHON_VERSION}" == "2.7" ]; then
    pip install -rdev_requirements2.txt;
else
    pip install -rdev_requirements.txt;
fi

pip install .
