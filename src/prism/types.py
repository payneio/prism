from pathlib import PurePosixPath

METADATA_ROOT_DIR_NAME = ".prism"
BACKLINKS_NAME = "backlinks.txt"
TAGS_NAME = "tags.txt"
SEARCH_INDEX_DIR_NAME = ".search"


# A fundamental concept in Prism is the PrismPath, which is a path relative to the
# filesystem root. This type is used throughout the filesystem interface to represent
# paths in a consistent way. The PrismPath type is a PathLike object, which means it
# can be a string, bytes, or a Path object. The PrismPath type is used in all methods
# that accept or return paths, and is normalized internally to use forward slashes.
class PrismPath(PurePosixPath):
    def endswith(self, suffix: str) -> bool:
        """Check if the path ends with the specified suffix."""
        return str(self).endswith(suffix)
