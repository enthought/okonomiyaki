from distutils.core import setup

if __name__ == "__main__":
    setup(name="okonomiyaki",
          author="David Cournapeau",
          author_email="David Cournapeau",
          packages=["okonomiyaki",
                    "okonomiyaki.models",
                    "okonomiyaki.utils",
                    "okonomiyaki.tests"]
    )
