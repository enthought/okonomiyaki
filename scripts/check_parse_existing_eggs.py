from __future__ import print_function

from argparse import ArgumentParser
import os
import sys

from haas.loader import Loader
from haas.testing import unittest
from haas.result import ResultCollecter
from haas.plugins.result_handler import (
    StandardTestResultHandler as BaseStandardTestResultHandler,
    VerboseTestResultHandler)
from haas.plugins.runner import BaseTestRunner

from okonomiyaki.file_formats import EggMetadata


ARTEFACT_TYPE_EGG = "egg"
DIRECTORY_TO_TYPE = {
    "eggs": ARTEFACT_TYPE_EGG,
}


class StandardTestResultHandler(BaseStandardTestResultHandler):

    def __call__(self, result):
        super(StandardTestResultHandler, self).__call__(result)
        if self.tests_run % 120 == 0:
            self.stream.write('\n')
            self.stream.flush()


def path_to_triple(path, root):
    """Given a full path, returns a quadruplet (organization, repository,
    platform)

    Parameters
    ----------
    path : path
        The full path of an artefact
    root : path
        The full path of the import directory's root

    Returns
    -------
    organization : str
        The organization name
    repository : str
        The repository name
    platform : str
        The platform (e.g. 'rh5-32')

    """
    relpath = os.path.relpath(path, root)
    parts = os.path.normpath(relpath).split(os.sep)
    if len(parts) < 4:
        raise ValueError(
            "Import directory should follow "
            "$organization/$repository/$platform/$artefact_type/**/* "
            "structure: {}".format(path))
    else:
        organization, repository, platform, artefact_dir = parts[:4]
        return organization, repository, platform


def artefact_generator(import_dir):
    for root, dirs, files in os.walk(import_dir, followlinks=True):
        if len(files) > 0:
            path = os.path.join(root, files[0])
            organization, repository, platform = path_to_triple(
                path, import_dir)
            for f in files:
                if f.lower().endswith('.egg'):
                    yield organization, repository, platform, os.path.join(
                        root, f)


def make_test(organization, repository, platform, path):
    filename = os.path.basename(path)
    eggname, _ = os.path.splitext(filename)
    name, version, build = eggname.split('-')
    test_name = 'test_{}_{}_{}_{}_v{}_build{}'.format(
        organization, repository, platform, name, version, build,
    ).replace(
        '-', '_',
    ).replace(
        '.', '_',
    )

    def test(self):
        EggMetadata.from_egg(path)

    return test_name, test


def generate_tests(import_dirs):
    print('Generating test cases...')
    for import_dir in import_dirs:
        cls_dict = {}
        for organization, repository, platform, path in artefact_generator(
                import_dir):
            test_name, test_case = make_test(
                organization, repository, platform, path)
            cls_dict[test_name] = test_case
        yield type('TestParsingEggs', (unittest.TestCase,), cls_dict)


def main(import_dirs, verbose):
    loader = Loader()
    test_suites = [loader.load_case(test_case)
                   for test_case in generate_tests(import_dirs)]
    suite = loader.create_suite(test_suites)
    test_count = suite.countTestCases()

    result_collector = ResultCollecter(buffer=False, failfast=False)

    if verbose:
        result_handler = VerboseTestResultHandler(test_count=test_count)
    else:
        result_handler = StandardTestResultHandler(test_count=test_count)

    result_collector.add_result_handler(result_handler)

    runner = BaseTestRunner()
    result = runner.run(result_collector, suite)
    return not result.wasSuccessful()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('directories', metavar='DIRECTORY', nargs='+')
    parser.add_argument('-v', '--verbose', action='store_true')

    ns = parser.parse_args(sys.argv[1:])

    sys.exit(main(ns.directories, ns.verbose))
