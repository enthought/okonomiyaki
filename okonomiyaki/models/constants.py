import collections

# This data representation is a bit stupid, but we keep it as is from
# buildware/epd_repo to make it easier to sync.
_SUBDIR = [
    # short     subdir                 arch     platform  osdist
    ('win-64', 'Windows/amd64',       'amd64', 'win32',   None),
    ('win-32', 'Windows/x86',         'x86',   'win32',   None),
    ('osx-64', 'MacOSX/amd64',        'amd64', 'darwin',  None),
    ('osx-32', 'MacOSX/x86',          'x86',   'darwin',  None),
    ('rh3-64', 'RedHat/RH3_amd64',    'amd64', 'linux2', 'RedHat_3'),
    ('rh3-32', 'RedHat/RH3_x86',      'x86',   'linux2', 'RedHat_3'),
    ('rh5-64', 'RedHat/RH5_amd64',    'amd64', 'linux2', 'RedHat_5'),
    ('rh5-32', 'RedHat/RH5_x86',      'x86',   'linux2', 'RedHat_5'),
    ('sol-64', 'Solaris/Sol10_amd64', 'amd64', 'sunos5', 'Solaris_10'),
    ('sol-32', 'Solaris/Sol10_x86',   'x86',   'sunos5', 'Solaris_10'),
]

_PlatformDescription = collections.namedtuple("_PlatformDescription", ["short", "subdir", "arch", "platform", "osdist"])

_PLATFORMS_DESCRIPTIONS = dict((line[0], _PlatformDescription(*line)) for line in _SUBDIR)
_PLATFORMS_SHORT_NAMES = tuple(line[0] for line in _SUBDIR)
