.. image:: https://travis-ci.org/enthought/okonomiyaki.png?branch=master
    :target: https://travis-ci.org/enthought/okonomiyaki

Okonomiyaki is an experimental library aimed at consolidating a lot of our
low-level code used for Enthought's eggs.

The library contains code for the following:

* producing EDM and enpkg-compatible egg from a tree + metadata
* object models for eggs metadata, as well as versions and platform
  representations

It works on both python 2 and 3, and pypy. It is expected to work on pretty
much any compliant python implementation.

Examples
========

Version parsing
---------------

To parse versions::

     from okonomiyaki.versions import EnpkgVersion
     # Every Version class has a from_string constructor
     v1 = EnpkgVersion.from_string("1.3.3-1")
     v2 = EnpkgVersion.from_string("1.3.2-3")

     assert v1 > v2

Version instances are designed to be immutable, and to be used as keys in
dictionaries.

Platform parsing
----------------

To parse epd platform strings (``rh5-64``, ``rh6_x86_64``, etc.) consistently::

    from okonomiyaki.platforms import EPDPlatform
    # Internal representation is normalized.
    rh5_new_name = EPDPlatform.from_string("rh5-x86_64")
    rh5_old_name = EPDPlatform.from_string("rh5-64")

    assert rh5_old_name == rh5_new_name

As for Version instances, ``EPDPlatform`` instances are designed to be
immutable and to be used as keys in dictionaries.

Egg metadata
------------

To parse Enthought eggs::

    from okonomiyaki.file_formats import EggMetadata

    # Only works for Enthought eggs
    metadata = EggMetadata.from_egg("numpy-1.10.1-1.egg")
    print(metadata.metadata_version)
    print(metadata.name)
    print(metadata.version)

This will take care of a lot of low-level, legacy details you don't want to
know about.
