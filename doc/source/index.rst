.. okonomiyaki documentation master file, created by
   sphinx-quickstart on Thu Oct 10 18:16:46 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to okonomiyaki's documentation!
=======================================

Okonomiyaki is a small library to deal with Enthought's specific
packaging, platform and index formats. The goal is to consolidate our
multiple implementations of the same formats into one library.

Example::

    # parsing epd platform strings
    from okonomiyaki.platforms import EPDPlatform

    epd_platform = EPDPlatform.from_epd_string("rh5-32")
    assert epd.platform == "rh5"
    assert epd.arch_bits == "32"
    assert epd.arch == "x86"

    # creating legacy s3 index entries
    from okonomiyaki.repositories import EnpkgS3IndexEntry

    s3_index_entry = EnpkgS3IndexEntry.from_egg("numpy-1.7.1-1.egg")
    print(s3_index_entry.size)
    print(s3_index_entry.packages) # dependencies

As its version suggests, it is still experimental and its API may change
in backward-incompatible ways.

.. include:: contents.rst.inc
