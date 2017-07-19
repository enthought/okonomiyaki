#! /bin/sh
set -e

pip install -U pip
pip install -rdev_requirements.txt;
pip install .
