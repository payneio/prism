from os import PathLike
from pathlib import Path

from .. import METADATA_ROOT_DIR_NAME
from ..exceptions import PrismNotFoundError


def has_prism_metadata(path: Path) -> bool:
    """Check if the given path contains Prism metadata"""
    return (path / METADATA_ROOT_DIR_NAME).exists()


def find_prism_root(start_path: PathLike = Path.cwd()) -> Path:
    """Find the root of the Prism repository by looking for .prism file"""

    path = Path(start_path)
    current = path.resolve()

    if has_prism_metadata(current):
        return current

    while current != current.parent:
        if has_prism_metadata(current):
            return current
        current = current.parent
    raise PrismNotFoundError("Could not find Prism root")
