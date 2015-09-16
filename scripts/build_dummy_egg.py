import argparse
import os.path
import sys

from okonomiyaki.file_formats import EggBuilder, EggMetadata
from okonomiyaki.platforms import EPDPlatform


def dummy_egg_from_egg(existing_egg, force=False, platform=None):
    metadata = EggMetadata.from_egg(existing_egg)
    if platform is not None:
        metadata.platform = platform

    if os.path.exists(metadata.egg_name):
        if force:
            os.unlink(metadata.egg_name)
        else:
            raise ValueError(
                "file {0!r} already exists.".format(metadata.egg_name)
            )

    metadata.metadata_version_info = (1, 3)
    with EggBuilder(metadata) as builder:
        pass

    return metadata.egg_name


def main(argv=None):
    argv = argv or sys.argv[1:]

    p = argparse.ArgumentParser()
    p.add_argument("-f", "--force", action="store_true")
    p.add_argument("--platform")
    p.add_argument("egg")

    ns = p.parse_args(argv)

    if ns.platform is None:
        platform = None
    else:
        platform = EPDPlatform.from_epd_string(ns.platform)

    path = dummy_egg_from_egg(ns.egg, force=ns.force, platform=platform)


if __name__ == "__main__":
    main()
