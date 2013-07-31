from distutils.core import setup

from okonomiyaki import __version__

if __name__ == "__main__":
    setup(name="okonomiyaki",
          author="David Cournapeau",
          author_email="David Cournapeau",
          packages=["okonomiyaki",
                    "okonomiyaki.bundled",
                    "okonomiyaki.bundled.ipython_utils",
                    "okonomiyaki.bundled.ipython_utils.tests",
                    "okonomiyaki.file_formats",
                    "okonomiyaki.file_formats.tests",
                    "okonomiyaki.models",
                    "okonomiyaki.models.tests",
                    "okonomiyaki.utils",
                    ],
          version=__version__
    )
