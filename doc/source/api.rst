.. _api:

===
API
===

.. module:: okonomiyaki

Only the below API should be considered public.

Enthought egg features
======================

.. currentmodule:: okonomiyaki.file_formats

EggMetadata class
-----------------

This models the metadata of an Enthought egg::

    metadata = EggMetadata.from_egg("numpy-1.7.1-1.egg")
    print(metadata.platform_tag)

.. autoclass:: EggMetadata
   :members:

EggBuilder class
----------------

This is a class to build Enthought eggs from an install tree

.. autoclass:: EggBuilder
    :members:
    :inherited-members:

EggRewriter class
-----------------

This is a class to build Enthought eggs from an existing setuptools egg.

.. autoclass:: EggRewriter
    :members:
    :inherited-members:

Runtimes
========

.. currentmodule:: okonomiyaki.runtimes


Runtime metadata factory
------------------------

This class allows you to parse edm runtime format, through its factory class
methods.

.. autoclass:: IRuntimeMetadata
    :members:

Platforms representations
=========================

.. currentmodule:: okonomiyaki.platforms

The main API is EPDPlatform. You can either create an explicit platform,
or try to guess the platform from the running system::

    platform = EPDPlatform.from_epd_string("rh5-32")
    platform = EPDPlatform.from_running_system()

One can access details through EPDPlatform instances' attributes.

.. autoclass:: EPDPlatform
   :members:

Generic platform representations are available through the `Platform`
class.

.. autoclass:: Platform
    :members:

Version representations
=======================

.. currentmodule:: okonomiyaki.versions

Each class has a `from_string` constructor to build the corresponding object
from its string representation. Those classes are designed to compare versions
between them (intra class, you obviously cannot compare a version from one kind
to a version of a different kind).

To manipulate versions in Enthought' eggs, you should use :py:class:`EnpkgVersion`.

.. autoclass:: PEP440Version
   :members:

.. autoclass:: EnpkgVersion
   :members:

.. autoclass:: SemanticVersion
   :members:

.. autoclass:: MetadataVersion
   :members:
