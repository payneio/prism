from pathlib import Path

import asyncclick as click

from prism import Disk, Page, Prism, PrismNotFoundError


@click.group()
def page():
    """Page operations"""
    pass


@page.command()
@click.argument("path", type=click.Path(path_type=Path), required=False)
@click.option("--title", "-t", help="Custom title for the page (defaults to path stem)")
async def add(path: str, title: str | None):
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
        drive = Disk.find_prism_drive()
    except PrismNotFoundError:
        raise click.ClickException("No prism found in current directory")

    try:
        prism = Prism(drive)
        absolute_path = Path(path).resolve() if path else Path.cwd()
        prism_path = await prism.drive.prism_path(absolute_path)
        page = await Page.create(drive=prism.drive, path=prism_path, title=title)
        click.echo(f"Created page at {page.path} with title: {title}")

    except Exception as e:
        raise click.ClickException(str(e))


@page.command()
@click.argument("path", type=click.Path())
async def refresh(path: str):
    """Refresh a page (run generators, update metadata)"""
    try:
        drive = Disk.find_prism_drive()
    except PrismNotFoundError:
        raise click.ClickException("No prism found in current directory")

    try:
        prism = Prism(drive)
        await prism.refresh_page(path)
        click.echo("Refreshed page.")
    except Exception as e:
        raise click.ClickException(str(e))
