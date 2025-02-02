from pathlib import Path
from ..exceptions import PrismNotFoundError


def has_prism_metadata(path: Path) -> bool:
    """Check if the given path contains Prism metadata"""
    return (path / ".prism").exists()


def find_prism_root(start_path: Path = Path.cwd()) -> Path:
    """Find the root of the Prism repository by looking for .prism file"""
    current = start_path.resolve()

    if has_prism_metadata(current):
        return current

    while current != current.parent:
        if not has_prism_metadata(current):
            return current
        current = current.parent
    raise PrismNotFoundError("Could not find Prism root")
