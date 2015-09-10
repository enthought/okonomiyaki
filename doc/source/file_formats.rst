.. _file_formats:

Runtimes
========

Conceptually, runtimes are packages that contain a specific language
interpreter/compiler. For example, Enthought may provide a python 2.7.10
runtime, or a pypy-based runtime.

Concretely, runtimes are simple zipfiles containing the files required for the
interpreter to work, its standard library, etc... It generally is fairly close
to the upstream distribution of the interpreter, e.g. a python runtime on
windows will be fairly close to a python installed from the python.org msi
package.

The format is as follows::

    <runtime_file>/enthought/runtime.json
    <runtime_file>/...

where the ``enthought/runtime.json`` file contains some metadata for Enthought
tools to understand the runtime. Every other file is simply unpacked as is in
the installation prefix.

The ``enthought/runtime.json`` MUST follow the json schemas as defined in
okonomiyaki.runtimes.runtime_schema. Each language has a common set of
attributes, plus an optional set of language-specific attributes.

For example, a windows julia runtime following the metadata version "1.0" may
look as follows::

    {
        "metadata_version": "1.0",
    
        "language": "julia",
        "implementation": "default",
        "version": "0.3.11+1",
        "language_version": "0.3.11",
        "platform": "win_x86_64",
    
        "build_revision": "483dbf5279",
    
        "executable": "${prefix}\\bin\\julia.exe",
        "paths": ["${prefix}\\bin"],
        "post_install": []
    }

When installed, jaguar will automatically fillup the ``${}`` variables from the
installation prefix.
