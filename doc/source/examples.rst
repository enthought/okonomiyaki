========
Examples
========

This section highlights the main APIs through some simple examples.

Platform
========

You can use the `~okonomiyaki.platforms.Platform` class to model platform
details in a consistent way on every supported OS by Enthought.

The easiest way to create instances is through the special constructors, e.g.::

    >>> from okonomiyaki.platforms import Platform

    >>> platform = Platform.from_running_system()
    >>> print(platform)
    'Ubuntu 14.10 on x86_64'

Platform instances have useful attributes to query the OS details::

    >>> platform.name
    'ubuntu'
    >>> platform.family
    'debian'
    >>> platform.os  # The most generic label
    'linux'

Or architecture (this example is 32 bits python running on 64 bits system)::

    >>> platform.arch.name  # The architecture of the running python
    'x86'
    >>> platform.machine.name  # The architecture of the running system
    'x86_64'

Platform instances are immutable and hashable.
