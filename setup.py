from distutils.core import setup

from okonomiyaki import __version__

if __name__ == "__main__":
    setup(name="okonomiyaki",
          author="David Cournapeau",
          author_email="David Cournapeau",
          packages=["okonomiyaki",
                    "okonomiyaki.file_formats",
                    "okonomiyaki.models",
                    "okonomiyaki.utils",
                    "okonomiyaki.tests"],
          version=__version__
    )
