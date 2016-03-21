import argparse
import sys

from ..file_formats import EggMetadata
from ..versions import MetadataVersion


def pkg_info(ns):
    metadata = EggMetadata._from_egg(ns.path, ns.sha256)
    if metadata.pkg_info is None:
        print("No PKG-INFO")
        sys.exit(-1)
    else:
        print(metadata.pkg_info.to_string().rstrip())


def spec_depend(ns):
    metadata = EggMetadata._from_egg(ns.path, ns.sha256)
    if ns.metadata_version is not None:
        metadata.metadata_version = MetadataVersion.from_string(
            ns.metadata_version
        )
    print(metadata.spec_depend_string.rstrip())


def summary(ns):
    metadata = EggMetadata._from_egg(ns.path, ns.sha256)
    print(metadata.summary.rstrip())


def main(argv=None):
    argv = argv or sys.argv[1:]

    p = argparse.ArgumentParser(
        description="description: query Enthought egg metadata."
    )
    subparsers = p.add_subparsers()

    spec_depend_p = subparsers.add_parser(
        "spec-depend",
        help="Show spec/depend metadata"
    )
    spec_depend_p.add_argument("path")
    spec_depend_p.add_argument(
        "--metadata-version",
        help="If given, the metadata version to use to output the spec/depend"
    )
    spec_depend_p.add_argument(
        "--sha256",
        help="Inject the given sha256 instead of calculating it from the "
             "given egg"
    )
    spec_depend_p.set_defaults(func=spec_depend)

    pkg_info_p = subparsers.add_parser(
        "pkg-info",
        help="Show PKG-INFO metadata"
    )
    pkg_info_p.add_argument("path")
    pkg_info_p.add_argument(
        "--sha256",
        help="Inject the given sha256 instead of calculating it from the "
             "given egg"
    )
    pkg_info_p.set_defaults(func=pkg_info)

    summary_p = subparsers.add_parser(
        "summary", help="Show spec/summary"
    )
    summary_p.add_argument("path")
    summary_p.add_argument(
        "--sha256",
        help="Inject the given sha256 instead of calculating it from the "
             "given egg"
    )
    summary_p.set_defaults(func=summary)

    ns = p.parse_args(argv)
    ns.func(ns)
