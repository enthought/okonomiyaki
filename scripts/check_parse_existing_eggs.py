import hashlib
import os

import click

from haas.loader import Loader
from haas.testing import unittest
from haas.result import ResultCollecter
from haas.plugins.result_handler import (
    StandardTestResultHandler, VerboseTestResultHandler)
from haas.plugins.runner import BaseTestRunner

from hatcher.api import BroodClient, BroodBearerTokenAuth
from okonomiyaki.file_formats import EggMetadata


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def compute_md5(filename, block_size=16384):
    hasher = hashlib.md5()
    with open(filename, "rb") as fp:
        while True:
            data = fp.read(block_size)
            if data == b"":
                break
            hasher.update(data)
    return hasher.hexdigest()


def path_to_quadruplet(path, root):
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
        The platform (e.g. 'rh5-x86_64')
    python_tag : str
        The PEP425 Python Tag

    """
    relpath = os.path.relpath(path, root)
    parts = os.path.normpath(relpath).split(os.sep)
    if len(parts) < 4:
        raise ValueError(
            "Import directory should follow "
            "$organization/$repository/$platform/$python_tag/**/* "
            "structure: {}".format(path))
    else:
        organization, repository, platform, python_tag = parts[:4]
        return organization, repository, platform, python_tag


def artefact_generator(import_dir):
    for root, dirs, files in os.walk(import_dir, followlinks=True):
        if len(files) > 0:
            path = os.path.join(root, files[0])
            organization, repository, platform, python_tag = path_to_quadruplet(  # noqa
                path, import_dir)
            for f in files:
                if f.lower().endswith('.egg'):
                    yield (organization, repository, platform, python_tag,
                           os.path.join(root, f))


def make_test(organization, repository, platform, python_tag, path):
    filename = os.path.basename(path)
    eggname, _ = os.path.splitext(filename)
    name, version, build = eggname.split('-')
    test_name = 'test_{}_{}_{}_{}_{}_v{}_build{}'.format(
        organization, repository, platform, python_tag, name, version, build,
    ).replace(
        '-', '_',
    ).replace(
        '.', '_',
    )

    def test(self):
        EggMetadata.from_egg(path)

    return test_name, test


def generate_tests(import_dir):
    click.echo('Generating test cases...')
    cls_dict = {}
    for organization, repository, platform, python_tag, path in artefact_generator(  # noqa
            import_dir):
        test_name, test_case = make_test(
            organization, repository, platform, python_tag, path)
        cls_dict[test_name] = test_case
    return type('TestParsingEggs', (unittest.TestCase,), cls_dict)


def run_test(import_dir, verbose):
    loader = Loader()
    test_case = loader.load_case(generate_tests(import_dir))
    suite = loader.create_suite((test_case,))
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


def existing_egg_names(repo_platform_path):
    for root, dirs, files in os.walk(repo_platform_path, followlinks=True):
        for filename in files:
            yield filename, os.path.join(root, filename)


def update_eggs_for_repository(platform_repo, target_directory, org_name,
                               repo_name, platform, index):
    if len(index) == 0:
        return
    repo_path = os.path.join(target_directory, org_name, repo_name, platform)
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)

    repo_full = '{}/{}'.format(org_name, repo_name)

    existing_eggs = dict(existing_egg_names(repo_path))
    extra_eggs = set(existing_eggs) - set(index)
    for egg_name in extra_eggs:
        click.echo('Removing {!r} {!r} {!r}'.format(
            repo_full, platform, egg_name))
        os.unlink(existing_eggs[egg_name])
    for egg_name, index_entry in index.items():
        python_tag = str(index_entry['python_tag']).lower()
        python_tag_dir = os.path.join(repo_path, python_tag)
        if not os.path.exists(python_tag_dir):
            os.makedirs(python_tag_dir)
        egg_path = os.path.join(python_tag_dir, egg_name)
        if os.path.exists(egg_path):
            md5 = compute_md5(egg_path)
            if md5 != index_entry['md5']:
                os.unlink(egg_path)
        if not os.path.exists(egg_path):
            name = index_entry['name']
            version = index_entry['full_version']
            click.echo('Downloading {!r} {!r} {!r} {!r}'.format(
                repo_full, platform, python_tag, egg_name))
            platform_repo.download_egg(
                python_tag, name, version, python_tag_dir)


def update_test_data(target_directory, repositories, token):
    python_tag = 'cp27'
    auth = BroodBearerTokenAuth(token)
    client = BroodClient.from_url('https://packages.enthought.com', auth=auth)

    platforms = client.list_platforms()

    for repository in repositories:
        org_name, repo_name = repository.split('/')
        repo = client.organization(org_name).repository(repo_name)
        for platform in platforms:
            platform_repo = repo.platform(platform)
            index = platform_repo.egg_index(python_tag)
            update_eggs_for_repository(
                platform_repo, target_directory, org_name, repo_name, platform,
                index)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('target_directory', nargs=1)
@click.argument('repositories', nargs=-1)
@click.option('-t', '--token', envvar='HATCHER_TOKEN')
@click.option('-v', '--verbose', default=False, is_flag=True)
def main(target_directory, repositories, token, verbose):
    update_test_data(target_directory, repositories, token)
    run_test(target_directory, verbose)


if __name__ == '__main__':
    main()
