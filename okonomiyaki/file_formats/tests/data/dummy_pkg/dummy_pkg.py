import click


@click.command()
def cli():
    click.echo('Dummy output...')


if __name__ == '__main__':
    cli()
