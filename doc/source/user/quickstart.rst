.. _quickstart:

Quickstart
==========

Eager to get started? This page gives a good introduction in how to get
started with okonomiyaki.

Let's get started with some simple examples.

Querying a jaguar runtime
~~~~~~~~~~~~~~~~~~~~~~~~~

.. module:: okonomiyaki.file_formats

Begin by importing the :func:`runtime_metadata_factory
<okonomiyaki.file_formats.runtime_metadata_factory>` function::

    >>> from okonomiyaki.file_formats import runtime_metadata_factory

To query metadata of an existing runtime::

    >>> metadata = runtime_metadata_factory("python-cpython-2.7.10-1-rh5_x86_64.runtime")
    >>> print(metadata.implementation)

Every metadata instance shares the attributes of the class RuntimeMetadataV1,
but each instance may have additional attributes depending on the language.

Querying an Enthought egg metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Begin by importing the :class:`EggMetadata
<okonomiyaki.file_formats.EggMetadata>` class::

    >>> from okonomiyaki.file_formats import EggMetadata

Now, to query metadata of an existing egg::

    >>> metadata = EggMetadata.from_path("enstaller-4.8.4-1.egg")
    >>> print(metadata.name)
    enstaller
    >>> print(metadata.abi_tag)
    None


Packaging files into an Enthought egg
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to packages existing files into an egg, you should use the
EggBuilder class::

    from okonomiyaki.file_formats import EggBuilder

    with EggBuilder(metadata) as builder:
        builder.add_tree("./usr", "EGG-INFO/usr")

This will create an egg with the given metadata, adding every file in
"./usr" into the egg.

Repackaging an existing setuptools egg
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to create an Enthought egg from an existing setuptools egg,
you should use the EggRewriter class::

    from okonomiyaki.file_formats import EggBuilder

    # Create metadata using the EggMetadata class to add platform,
    # dependencies information
    with EggRewriter(metadata, "foo-2.3-py2.7.egg") as rewriter:
        rewriter.add_file("dummy.txt", "EGG-INFO/dummy.txt")

Platform representations
------------------------

.. module:: okonomiyaki.platforms

There are 2 main classes to deal with platform representations in
okonomiyaki, :class:`Platform <okonomiyaki.platforms.Platform>`
nd :class:`EPDPlatform <okonomiyaki.platforms.EPDPlatform>`.

Platform are generic representations, and provide a consistent API to
query various details about a given platform, that is an OS + architecture
+ machine combination::

    >>> from okonomiyaki.platforms import Platform
    >>> p = Platform.from_running_system()
    >>> print(p)
    'Mac OS X 10.10.3 on x86_64'
    >>> print(p.os)
    'darwin'
    >>> print(p.family)
    'mac_os_x'
    >>> print(p.release)
    '10.10.3'

Architectures and machines are often the same, but not always: the
platform for a program running in 64 bits on 32 bits Kernel OS X would
have a `x86_64` bits architecture on a `x86` bits machine. A 32 bits
process running on 64 bits would have a `x86` bits architecture and
`x86_64` bits machine.

Platform instances are immutable (though not enforced) and can be safely
hashed and compared.

EPDPlatform represents a given platform supported by Enthought.
Internally, its state is stored as a `Platform` instance, and it provides
various APIs that are specific to packaging.

    >>> from okonomiyaki.platforms import EPDPlatform
    >>> p = Platform.from_epd_string("rh5-32")
    >>> print(p.arch_bits)
    '64'
    >>> print(p.pep425_tag)
    'macosx_10_6_x86_64'
