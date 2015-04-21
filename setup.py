import os.path
import subprocess

from setuptools import setup

MAJOR = 0
MINOR = 5
MICRO = 1

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

    return git_revision


def write_version_py(filename):
    template = """\
# THIS FILE IS GENERATED FROM ENSTALLER SETUP.PY
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
        git_rev = git_version()
    elif os.path.exists(filename):
        # must be a source distribution, use existing version file
        try:
            from okonomiyaki._version import git_revision as git_rev
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing "
                              "{0} and the build directory "
                              "before building.".format(filename))
    else:
        git_rev = "Unknown"

    if not IS_RELEASED:
        fullversion += '.dev1-' + git_rev[:7]

    with open(filename, "wt") as fp:
        fp.write(template.format(version=VERSION,
                                 full_version=fullversion,
                                 git_revision=git_rev,
                                 is_released=IS_RELEASED))


def main():
    write_version_py("okonomiyaki/_version.py")

    from okonomiyaki import __version__

    package_data = {"okonomiyaki.repositories.tests": ["data/*egg"]}

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
          install_requires=["six"],
          license="BSD",
          version=__version__)

if __name__ == "__main__":
    main()
