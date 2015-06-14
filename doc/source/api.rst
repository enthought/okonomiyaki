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

EggBuilder class
----------------

This is a class to build Enthought eggs from an existing setuptools egg.

.. autoclass:: EggRewriter
    :members:
    :inherited-members:

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

Repositories format
===================

.. currentmodule:: okonomiyaki.repositories

Classes in this module model our different index entries.

GritsEggEntry can be used to automatically create the grits key, tags and
metadata from an egg package.

.. autoclass:: GritsEggEntry
    :members:
