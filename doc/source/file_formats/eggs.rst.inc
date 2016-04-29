====
Eggs
====

Enthought eggs are similar to setuptools' eggs, with some additions to deal
with non-python packages, static dependency specification, etc...

First, a few notations:

* $PREFIX: is understood as the prefix of the current python. In a standard
  install, $PREFIX/bin/python will be the python binary on unix,
  $PREFIX/python.exe on windows.
* $SCRIPTSDIR: where 'binaries' are installed. Generally $PREFIX/bin on Unix,
  $PREFIX\\Scripts on windows.
* $METADIR: package-specific directory where files/metadata get installed.
  Enpkg installs the metadata in $PREFIX/EGG-INFO/$package_name
* basename(path): the basename of that path (as computed by
  os.path.basename)

All the metadata are contained within the EGG-INFO subdirectory.  This
subdirectory contains all the metadata needed by egginst to install an egg
properly. Those are set within different free-format text files:

* EGG-INFO/inst/appinst.dat
* EGG-INFO/inst/files_to_install.txt
* EGG-INFO/spec/depend
* EGG-INFO/spec/lib-depend
* EGG-INFO/spec/lib-provide

EGG-INFO/spec/depend
====================

This is the most important file in Enthought eggs: it contains all the metadata
required to solve dependencies, and defines all the metadata to be used by the
deployment server and for indices as used by the packaging clients (hatcher,
enpkg, edm, etc.).

It is following a subset of the python syntax data, and should be parsed
through the :class:`EggMetadata <okonomiyaki.file_formats.EggMetadata>`
class. It is versioned, and every new minor version is designed to be backward
and forward compatible, that is it should always be possible to convert
metadata at version 1.M to 1.N with M < N and M > N. Concretely, this means:

* a new minor release may only add new fields (backward compatibility)
* every newly added field must have a reasonable default (forward
  compatibility)

You can use `python -m okonomiyaki spec-depend` to look at the conversion
between minor versions:

   .. code-block:: shell

      # By default, use the metadata version as used in the actual
      # EGG-INFO/spec/depend file.
      $ python -m okonomiyaki spec-depend numpy-1.9.2-3.egg
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
      # Looking at metadata_version '1.1
      $ python -m okonomiyaki spec-depend numpy-1.9.2-3.egg --metadata-version 1.1
      metadata_version = '1.1'
      name = 'numpy'
      version = '1.9.2'
      build = 3

      arch = 'amd64'
      platform = 'linux2'
      osdist = 'RedHat_5'
      python = '2.7'
      packages = [
        'MKL 11.1.4',
         'libgfortran 3.0.0',
      ]
      # Forward compatibility
      $ python -m okonomiyaki spec-depend numpy-1.9.2-3.egg --metadata-version 1.4
      metadata_version = '1.4'
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

      platform_abi = 'gnu'

      packages = [
        'MKL 11.1.4',
        'libgfortran 3.0.0',
      ]

        
Metadata version 1.1
--------------------

An example for the metadata version "1.1"::

    metadata_version = '1.1'
    name = 'numpy'
    version = '1.7.1'
    build = 3

    arch = 'x86'
    platform = 'linux2'
    osdist = 'RedHat_5'
    python = '2.7'
    packages = [
      'MKL 10.3-1',
    ]

Any metadata version "1.X" has the following fields:

- metadata_version: a string. It needs to be >= '1.1'. Formats up to 1.4 are
  currently defined. :class:`MetadataVersion <okonomiyaki.versions.MetadataVersion>`
  may be used to compare metadata version.
- name: a string. This is the name of the package. May use upper-case (e.g. for
  PIL, name will be 'PIL'). This is the name defined in our recipe.
- version: a string. The upstream version
- build: the build number
- arch/platform/osdist: those are not very consistent and should not be relied
  on.

    .. note:: those metadata are guessed from the egg content (See the code
            in workbench.spec.update_egg). I don't know what osdist is
            used for, and it can be None.

- python: the python version, or None. As for arch/platform/osdist, this is not
  set directly, but guessed by looking into the .pyc code inside the egg. As
  for the arch/platform/osdist, it is not very reliable or consistent.
- packages: a list of dependencies.  You will also note that name and version
  are space separated. The version part is actually optional.

Metadata version 1.2
--------------------

The metadata_version "1.2" introduces a single new field, `python_tag`,
following PEP425::

    metadata_version = '1.2'
    name = 'numpy'
    version = '1.9.2'
    build = 3

    arch = 'amd64'
    platform = 'linux2'
    osdist = 'RedHat_5'
    python = '2.7'
    python_tag = 'cp27'
    packages = [
      'MKL 11.1.4',
      'libgfortran 3.0.0',
    ]

`python_tag` is a text string, a defaults to `cpMN` where `M` and `N` are the
major/minor version of python, as defined in the `python` field.

.. note:: For non python eggs (e.g. a C library), python_tag may be None.

Metadata version 1.3
--------------------

This is the logical extension of "1.2", introducing the missing PEP425 tags
`platform_tag` and `abi_tag`. Example::

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

The default values for `platform_tag` is deduced from `platform`/`arch`, and
the default value for `abi_tag` is deduced from `python_tag` (as Enthought has
only used one the `cpMNm` ABI so far, there is no ambiguity)

.. note:: for the cases where no ABI or platform is defined (e.g. pure python
          egg), the corresponding tags may be set to `None`.

Metadata version 1.4
--------------------

This addes a new field `platform_abi`, in the same spirit as the PEP425 tags.
Example::

    metadata_version = '1.4'
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
    
    platform_abi = 'gnu'
    
    packages = [
      'MKL 11.1.4',
      'libgfortran 3.0.0',
    ]

This is used for ABIs defined outside python, e.g. a different C library on
Linux, or more practically, the MSVC ABI on Windows. For example, Qt built w/
MVSC 2008 would have `platform_abi = "msvc2008"`, one built with MSVC 2015,
`platform_abi = "msvc2015"`.

.. note:: `platform_abi` may be set to None, for eggs without any compiled
    code.

EGG-INFO/spec/summary
=====================

A copy of the Summary field in our pspec.xml. The code writing this is also in
workbench.spec.


EGG-INFO/spec/lib-depend
========================

Free-form text format, contains the consolidated output of ldd or otool -L of
each library/python extension.

EGG-INFO/spec/lib-provide
=========================

Free-form text format, contains the list of provided libraries in that egg.
While lib-depend unzip the egg to look for files, lib-provide uses the list of
files in files_to_install.txt and do a simple pattern matching to find out what
to write.

EGG-INFO/inst/appinst.dat
=========================

A python script that is used by 'applications' during the install process. Is
generally defined in the recipe files directory (as appinst.dat), and
explicitly included in our eggs through
`workbench.eggcreator.EggCreator.add_appinst_dat()`

Mostly used for setting up application shortcuts.

EGG-INFO/inst/files_to_install.txt
==================================

This file is used to define so-called proxies (a clumsy way to emulate
softlinks on windows) and support softlinks on non-windows platform. The file
defines one entry per line, and each entry is a space separated set of two
items.

On linux and os x, each entry looks as follows::

     EGG-INFO/usr/lib/libzmq.so                         libzmq.so.0.0.0

This defines a link join(prefix, 'lib/libzmq.so') to libzmq.so.0.0.0. More
precisely:

    - the left part is used to define the link name, the right part the target
      of the link.
    - the actual link name will be a join of the prefix + the part that comes
      after EGG-INFO/usr.

Entries may also look as follows::

     EGG-INFO/usr/bin/xslt-config                       False

This does not define a link to False, but instead tells egginst to ignore this
entry.

A third format only encountered on windows' eggs::

    {TARGET}  {ACTION}

where {TARGET} must be in the zip archive, and where {ACTION} may be one of the
following:

    - PROXY: a proxy to the left part is created. A proxy is a set of two
      files, both written in the $BINDIR

        - one small exe which is a copy of the setuptools' cli.exe, renamed to
          basename({TARGET}).
        - another file {TARGET_NO_EXTENSION}-script.py where
          TARGET_NO_EXTENSION = basename(splitext({TARGET}))

    - Anything else: understood as a directory. In that case, {TARGET} will be
      copied into $PREFIX\\{ACTION}\\basename({TARGET})

A PROXY example::

    EGG-INFO/usr/bin/ar.exe  PROXY

Egginst will create the following::

    # A copy of cli.exe
    $BINDIR\\ar.exe
    # the python script called by $BINDIR\\ar.exe, itself calling
    # $METADIR\\usr\\bin\\ar.exe
    $BINDIR\\ar-script.py

A non-PROXY example::

    EGG-INFO/usr/bin/ar.exe  EGG-INFO/mingw/usr/i686-w64-mingw32/bin

Egginst will create the following::
   
    # A copy of EGG-INFO/usr/bin/ar.exe
    $METADIR\\usr\\i686-w64-mingw32\\bin\\ar.exe

