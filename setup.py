import os.path
import re
import subprocess

from setuptools import setup

MAJOR = 0
MINOR = 8
MICRO = 0

IS_RELEASED = True

VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = (subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).
               communicate()[0])
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = "Unknown"

    try:
        out = _minimal_ext_cmd(['git', 'rev-list', '--count', 'HEAD'])
        git_count = out.strip().decode('ascii')
    except OSError:
        git_count = '0'

    return git_revision, git_count


def write_version_py(filename):
    template = """\
# THIS FILE IS GENERATED FROM OKONOMIYAKI SETUP.PY
version = '{version}'
full_version = '{full_version}'
git_revision = '{git_revision}'
is_released = {is_released}

if not is_released:
    version = full_version
"""
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of numpy.version messes up the build under Python 3.
    fullversion = VERSION
    if os.path.exists('.git'):
        git_rev, dev_num = git_version()
    elif os.path.exists(filename):
        # must be a source distribution, use existing version file
        try:
            from okonomiyaki._version import git_revision as git_rev
            from okonomiyaki._version import full_version as full_v
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing "
                              "{0} and the build directory "
                              "before building.".format(filename))

        match = re.match(r'.*?\.dev(?P<dev_num>\d+)', full_v)
        if match is None:
            dev_num = '0'
        else:
            dev_num = match.group('dev_num')
    else:
        git_rev = "Unknown"
        dev_num = "0"

    if not IS_RELEASED:
        fullversion += '.dev' + dev_num

    with open(filename, "wt") as fp:
        fp.write(template.format(version=VERSION,
                                 full_version=fullversion,
                                 git_revision=git_rev,
                                 is_released=IS_RELEASED))


def main():
    write_version_py("okonomiyaki/_version.py")

    from okonomiyaki import __version__

    package_data = {
        "okonomiyaki.repositories.tests": [
            "data/*egg", "data/broken_legacy_eggs/*egg", "data/*.txt",
        ],
    }

    setup(name="okonomiyaki",
          author="David Cournapeau",
          author_email="David Cournapeau",
          packages=["okonomiyaki",
                    "okonomiyaki.bundled",
                    "okonomiyaki.bundled.traitlets",
                    "okonomiyaki.file_formats",
                    "okonomiyaki.file_formats.tests",
                    "okonomiyaki.platforms",
                    "okonomiyaki.platforms.tests",
                    "okonomiyaki.repositories",
                    "okonomiyaki.repositories.tests",
                    "okonomiyaki.versions",
                    "okonomiyaki.versions.tests",
                    "okonomiyaki.utils",
                    ],
          package_data=package_data,
          install_requires=["six", "zipfile2 >= 0.0.5"],
          license="BSD",
          version=__version__)

if __name__ == "__main__":
    main()
