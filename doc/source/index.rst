.. okonomiyaki documentation master file, created by
   sphinx-quickstart on Thu Oct 10 18:16:46 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to okonomiyaki's documentation!
=======================================

Okonomiyaki is a small library to deal with Enthought's packaging
specificities. It includes:

* features to parse Enthought eggs and query their metadata
* various versions comparison algorithms (PEP440, PEP386, EnpkgVersion which is
  specific to Enthought's eggs)
* various utilities for platform detection
* a minimalistic CLI to query egg metadata from the command line.

Example::

    $ python -m okonomiyaki --spec-depend numpy-1.9.2-3.egg
    metadata_version = '1.3'
    name = 'numpy'
    version = '1.9.2'
    build = 3

    arch = 'amd64'
    platform = 'linux2'
    osdist = 'RedHat_5'
    python = '2.7'

    python_tag = 'cp27'
    abi_tag = 'cp27m'
    platform_tag = 'linux_x86_64'

    packages = [
      'MKL 11.1.4',
      'libgfortran 3.0.0',
    ]

As its version suggests, it is still experimental and its API may change in
backward-incompatible ways.

.. include:: contents.rst.inc
