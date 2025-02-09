from pathlib import Path

import asyncclick as click

from prism import Disk, Prism, PrismNotFoundError, PrismPath

from .folder import folder
from .page import page


@click.group()
def cli():
    """Prism - Next-generation content management"""
    pass


cli.add_command(page)
cli.add_command(folder)


@cli.command()
@click.argument("path", type=click.Path(), default=".")
async def init(path: str):
    """Initialize a new Prism repository"""

    target = Path(path).resolve()
    try:
        await Prism.initialize(target)
    except Exception as e:
        raise click.ClickException(str(e))

    click.echo(f"Initialized Prism repository in {target}.")


@cli.command()
async def refresh():
    """Refresh all folders and pages in the current repository"""

    try:
        drive = Disk.find_prism_drive()
    except PrismNotFoundError:
        raise click.ClickException("No prism found in current directory")

    try:
        prism = Prism(drive)
        await prism.refresh_folder(PrismPath(), recursive=True)
        click.echo("Refreshed all pages.")
    except Exception as e:
        raise click.ClickException(str(e))


if __name__ == "__main__":
    cli()
