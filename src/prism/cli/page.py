from pathlib import Path
import click
from ..prism import Prism
from ..utils.paths import find_prism_root


@click.group()
def page():
    """Page operations"""
    pass


@page.command()
@click.argument("path", type=click.Path())
@click.option("--title", "-t", help="Custom title for the page (defaults to path stem)")
def add(path: str, title: str | None):
    """Add a new page at the specified path"""
    try:
        prism = Prism(find_prism_root())
        page_path = Path(path)

        # Create parent folders if needed
        parent = page_path.parent
        if parent != Path("."):
            folder = prism.get_folder(parent)
        else:
            folder = prism.get_folder(".")

        # Create the page
        folder.create_page(filename=page_path.name, title=title)
        click.echo("Created page.")
    except Exception as e:
        raise click.ClickException(str(e))


@page.command()
@click.argument("path", type=click.Path())
def refresh(path: str):
    """Refresh a page (run generators, update metadata)"""
    try:
        prism = Prism(find_prism_root())
        prism.refresh_page(path)
        click.echo("Refreshed page.")
    except Exception as e:
        raise click.ClickException(str(e))
