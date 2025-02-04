from pathlib import Path

import click

from ..prism import Page, Prism
from ..utils.paths import find_prism_root


@click.group()
def page():
    """Page operations"""
    pass


@page.command()
@click.argument("path", type=click.Path(), required=False, default=Path.cwd())
@click.option("--title", "-t", help="Custom title for the page (defaults to path stem)")
def add(path: str, title: str | None):
    """Add a new page at the specified path.

    - Either a filename in the path or title must be provided.
    - The path is relative to the current working directory.
    - If path is not provided, title will be used to generate a filename in
        the current directory.
    - If content is not provided, a default template will be used.
    - If title is not provided, the filename will be converted to a title
        and be used in the template for the new page.
    """
    try:
        page_path = Path(path)
        name = page_path.name

        if not name and not title:
            raise click.ClickException("Either filename or title must be provided")

        Page.create(path=page_path.name, title=title)
        click.echo(f"Created page at {page_path} with title: {title}")

    except Exception as e:
        raise click.ClickException(str(e))


@page.command()
@click.argument("path", type=click.Path())
def refresh(path: str):
    """Refresh a page (run generators, update metadata)"""
    try:
        prism = Prism()
        prism.refresh_page(path)
        click.echo("Refreshed page.")
    except Exception as e:
        raise click.ClickException(str(e))
