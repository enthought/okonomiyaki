from setuptools import setup

from okonomiyaki import __version__

if __name__ == "__main__":
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
                    "okonomiyaki.utils",
                    ],
          install_requires=["six"],
          license="BSD",
          version=__version__
    )
