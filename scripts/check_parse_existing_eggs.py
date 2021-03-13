import os

import click

from haas.loader import Loader
from haas.testing import unittest
from haas.result import ResultCollecter
from haas.plugins.result_handler import (
    StandardTestResultHandler as BaseStandardTestResultHandler,
    VerboseTestResultHandler)
from haas.plugins.runner import BaseTestRunner

from hatcher.core.brood_url_handler import BroodURLHandler
from hatcher.core.brood_client import BroodClient
from hatcher.core.auth import BroodClientAuth
from hatcher.errors import ChecksumMismatchError
from okonomiyaki.file_formats import EggMetadata
from okonomiyaki.utils import compute_sha256


class StandardTestResultHandler(BaseStandardTestResultHandler):

    def __call__(self, result):
        super(StandardTestResultHandler, self).__call__(result)
        if self.tests_run % 120 == 0:
            padding = len(str(self._test_count))
            newline = ' ({run: >{padding}d}/{total:d})\n'.format(
                run=self.tests_run,
                padding=padding,
                total=self._test_count,
            )
            self.stream.write(newline)
            self.stream.flush()


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


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


def make_test(organization, repository, platform, python_tag, path, strict):
    filename = os.path.basename(path)
    eggname, _ = os.path.splitext(filename)
    name, version, build = eggname.split('-')
    strictness = '' if strict else '_relaxed_unicode'
    test_name = 'test_{}_{}_{}_{}_{}_v{}_build{}{}'.format(
        organization, repository, platform, python_tag,
        name, version, build, strictness).replace('-', '_').replace('.', '_')

    def test(self):
        EggMetadata.from_egg(path, strict=strict)

    return test_name, test


def generate_tests(import_dir, repository_spec, strict):
    cls_dict = {}
    filter_org, filter_repo = repository_spec.split('/')
    for organization, repository, platform, python_tag, path in artefact_generator(  # noqa
            import_dir):
        if organization == filter_org and repository == filter_repo:
            test_name, test_case = make_test(
                organization, repository, platform, python_tag, path, strict)
            cls_dict[test_name] = test_case
    class_name = 'TestParsingEggs_{}_{}'.format(filter_org, filter_repo)
    return type(class_name, (unittest.TestCase,), cls_dict)


def run_test(import_dir, repositories, verbose, strict):
    loader = Loader()

    click.echo('Generating test cases...')

    test_cases = [
        loader.load_case(generate_tests(import_dir, repository, strict))
        for repository in repositories
    ]
    suite = loader.create_suite(test_cases)
    click.echo('Done.')

    test_count = suite.countTestCases()
    if verbose:
        result_handler = VerboseTestResultHandler(test_count=test_count)
    else:
        result_handler = StandardTestResultHandler(test_count=test_count)

    result_collector = ResultCollecter(buffer=False, failfast=False)
    result_collector.add_result_handler(result_handler)

    runner = BaseTestRunner()
    result = runner.run(result_collector, suite)
    return result.wasSuccessful()


def existing_egg_names(repo_platform_path):
    for root, dirs, files in os.walk(repo_platform_path, followlinks=True):
        for filename in files:
            yield filename, os.path.join(root, filename)


def _retry_download_if_fails(
        platform_repo, python_tag, name, version, python_tag_dir, tries=3):
    try_number = 0
    while try_number < tries:
        try:
            platform_repo.download_egg(
                python_tag, name, version, python_tag_dir)
        except ChecksumMismatchError:
            try_number += 1
            if try_number < tries:
                click.echo(
                    'Download failed due to mismatched checksum; retrying.')
            else:
                raise
        else:
            return


def update_eggs_for_repository(
        platform_repo, target_directory, org_name, repo_name, platform, index):

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
            if compute_sha256(egg_path) != index_entry['sha256']:
                os.unlink(egg_path)
        if not os.path.exists(egg_path):
            name = index_entry['name']
            version = index_entry['full_version']
            click.echo('Downloading {!r} {!r} {!r} {!r}'.format(
                repo_full, platform, python_tag, egg_name))
            _retry_download_if_fails(
                platform_repo, python_tag, name, version, python_tag_dir)


def update_test_data(target_directory, repositories, token, python_tag):
    client = get_brood_client('https://packages.enthought.com', token)
    platforms = client.list_platforms()
    for repository in repositories:
        org_name, repo_name = repository.split('/')
        repo = client.organization(org_name).repository(repo_name)
        for platform in platforms:
            platform_repo = repo.platform(platform)
            index = platform_repo.egg_index(python_tag)
            click.echo('Updating repository {!r} for platform {!r}'.format(
                repository, platform))
            update_eggs_for_repository(
                platform_repo, target_directory, org_name, repo_name, platform, index)


def get_brood_client(url, token=None):
    if token is None:
        auth = None
    else:
        auth = BroodClientAuth(url, token)
    url_handler = BroodURLHandler.from_auth(url, auth=auth)
    return BroodClient(url_handler=url_handler, api_version=1)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('target_directory', nargs=1)
@click.argument('repositories', nargs=-1)
@click.option('--python', default='cp36')
@click.option('-t', '--token', envvar='HATCHER_TOKEN')
@click.option('-v', '--verbose', default=False, is_flag=True)
@click.option('--strict/--no-strict', default=True)
@click.pass_context
def main(ctx, target_directory, repositories, python, token, verbose, strict):
    eggs_directory = os.path.join(target_directory, python)
    if not os.path.exists(eggs_directory):
        os.makedirs(eggs_directory)
    update_test_data(eggs_directory, repositories, token, python)
    successful = run_test(eggs_directory, repositories, verbose, strict)
    ctx.exit(0 if successful else 1)


if __name__ == '__main__':
    main()
