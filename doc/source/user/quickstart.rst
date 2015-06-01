.. _quickstart:

Quickstart
==========

.. module:: okonomiyaki.file_formats

Eager to get started? This page gives a good introduction in how to get
started with okonomiyaki.

Let's get started with some simple examples.


Querying an Enthought egg metadata
----------------------------------

Begin by importing the EggMetadata class::

    >>> from okonomiyaki.file_formats import EggMetadata

Now, to query metadata of an existing egg::

    >>> metadata = EggMetadata.from_path("enstaller-4.8.4-1.egg")
    >>> print(metadata.name)
    enstaller
    >>> print(metadata.abi_tag)
    None


Packaging files into an Enthought egg
-------------------------------------

If you want to packages existing files into an egg, you should use the
EggBuilder class::

    from okonomiyaki.file_formats import EggBuilder

    with EggBuilder(metadata) as builder:
        builder.add_tree("./usr", "EGG-INFO/usr")

This will create an egg with the given metadata, adding every file in
"./usr" into the egg.
