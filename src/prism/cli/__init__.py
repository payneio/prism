# src/prism/cli/__init__.py
from pathlib import Path
import click
from .page import page
from .folder import folder
from textwrap import dedent
from ..prism import Prism
from ..utils.paths import find_prism_root


@click.group()
def cli():
    """Prism - Next-generation content management"""
    pass


cli.add_command(page)
cli.add_command(folder)


@cli.command()
@click.argument("path", type=click.Path(), default=".")
def init(path: str):
    """Initialize a new Prism repository"""

    target = Path(path).resolve()
    try:
        Prism.initialize(target)
    except Exception as e:
        raise click.ClickException(str(e))

    click.echo(f"Initialized Prism repository in {target}.")


@cli.command()
def refresh():
    """Refresh all folders and pages in the current repository"""

    prism_root: Path = find_prism_root()
    if not prism_root:
        raise click.ClickException("No prism found in current directory")

    try:
        prism = Prism(prism_root)
        prism.refresh_folder(".", recursive=True)
        click.echo("Refreshed all pages.")
    except Exception as e:
        raise click.ClickException(str(e))
