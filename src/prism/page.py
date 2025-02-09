# src/prism/core/page.py
import asyncio
import re
from os import PathLike
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Dict, Optional

import yaml

from .exceptions import PrismError
from .filesystem import FileSystem, PrismPath
from .generators.breadcrumbs import BreadcrumbsGenerator
from .generators.pages import PagesGenerator
from .generators.siblings import SiblingsGenerator
from .generators.toc import TocGenerator

if TYPE_CHECKING:
    from .generators.base import Generator


class PageError(PrismError):
    """Base class for page-related errors"""

    pass


class PageValidationError(PageError):
    """Raised when page structure validation fails"""

    pass


METADATA_BEGIN = "<!-- prism:metadata\n---"
METADATA_END = "---\n-->"
GENERATOR_PATTERN = re.compile(
    r"<!--\s*prism:generate:(\w+)\s*-->(.*?)<!--\s*/prism:generate:\1\s*-->",
    re.DOTALL,
)


class Page:
    """Represents a single page in a Prism repository"""

    drive: FileSystem
    path: PrismPath
    _content: str | None = None
    _metadata: Dict[str, Any] | None = None
    _title: str | None = None

    @staticmethod
    async def create(
        drive: FileSystem,
        path: PrismPath | None = None,
        title: str | None = None,
        content: str | None = None,
    ) -> "Page":
        """Create a new page.

        - Either path or title must be provided.
        - The path is relative to the current working directory.
        - If path is not provided, title will be used to generate a filename in
        the current directory.
        - If content is not provided, a default template will be used.
        - If title is not provided, the filename will be converted to a title
        and be used in the template for the new page.
        """
        if path and not isinstance(path, PrismPath):
            raise ValueError("Use PrismPaths when you create a page!")

        if path is None and title is None:
            raise PageError("Filename or title must be provided")

        if path is None:
            path = PrismPath(title.lower().replace(" ", "_") + ".md")

        # Ensure .md extension.
        path = path.with_suffix(".md")

        # Check if page already exists.
        if await drive.exists(path):
            raise PageError(f"Page already exists: {path}")

        # Generate a title if necessary.
        if title is None:
            # Convert PrismPath to string, remove extension, and format
            path_str = str(path.with_suffix(""))
            title = path_str.replace("_", " ").title()

        # Create the default content if none provided
        if content is None:
            content = dedent(f"""
                # {title}

                <!-- prism:generate:breadcrumbs -->
                <!-- /prism:generate:breadcrumbs -->

                ## Pages

                <!-- prism:generate:pages -->
                <!-- /prism:generate:pages -->

                ...

                <!-- prism:metadata
                ---
                title: {title}
                ---
                -->

            """).lstrip()

        # Write the page content (creates subdirectories if needed).
        await drive.write(path, content)
        page = Page(drive, path)
        await page.refresh()
        return page

    def __init__(self, drive: FileSystem, path: PrismPath):
        self.drive = drive
        self.path = path

    # CACHE METHODS

    async def _clear_cache(self):
        """Clear cached properties"""
        self._content = None
        self._metadata = None
        self._title = None

    async def _load(self) -> "Page":
        """Load page properties from disk"""
        self._content = await self.drive.read(self.path)

        # Extract title from content.
        match = re.search(r"^#\s+(.+)$", self._content, re.MULTILINE)
        if not match:
            raise PageValidationError(f"No title (h1) found in {self.path}")
        self._title = match.group(1).strip()

        # Extract metadata from content.
        self._metadata = self._parse_metadata()

        return self

    async def _save(self):
        """Save changes back to disk"""
        if self._content is not None:
            await self.drive.write(self.path, self._content)
            self._content = None  # Reset cache

    # PROPERTIES

    @property
    async def content(self) -> str:
        """Get page content, loading from disk if needed"""
        if self._content is None:
            await self._load()
        return self._content

    @property
    async def title(self) -> str:
        """Get the page title (first h1)"""
        if self._title is None:
            await self._load()
        return self._title

    @property
    async def metadata(self) -> Dict[str, Any]:
        """Get page metadata, parsing if needed"""
        if self._metadata is None:
            await self._load()
        return self._metadata

    def _metadata_indices(self) -> tuple[int, int]:
        # Grab all content between <!-- prism:metadata --> markers.
        content = self._content
        metadata_start = content.find(METADATA_BEGIN)
        metadata_end = content.find(METADATA_END)
        return metadata_start, metadata_end

    def _has_metadata(self) -> bool:
        """Check if the page has a metadata section"""
        metadata_start, metadata_end = self._metadata_indices()
        return not (metadata_start == -1 or metadata_end == -1)

    def _parse_metadata(self) -> Dict[str, Any]:
        """Parse YAML metadata from the bottom of the file"""
        if not self._has_metadata():
            return {}
        metadata_start, metadata_end = self._metadata_indices()
        metadata_copy = self._content[
            metadata_start + len(METADATA_BEGIN) : metadata_end
        ].strip()
        try:
            return yaml.safe_load(metadata_copy)
        except yaml.YAMLError as e:
            raise PageError(f"Invalid metadata YAML in {self.path}: {e}")

    def _update_metadata(self):
        """Update page metadata"""
        current_metadata = (self._metadata or {}).copy()

        # Update standard metadata fields
        new_metadata = {
            "title": self._title,
            "path": self.path,
            "generator_types": self._find_generator_types(),
        }
        current_metadata.update(new_metadata)

        # Format as YAML with specific styling
        metadata_yaml = ""
        for key, value in current_metadata.items():
            if key == "generator_types":
                if value and len(value) > 0:  # If we have generators
                    metadata_yaml += f"{key}:\n"
                    for gen_type in value:
                        metadata_yaml += f"  - {gen_type}\n"
                else:
                    metadata_yaml += f"{key}:\n"  # Empty list
            else:
                metadata_yaml += f"{key}: {value}\n"

        # Update page content with new metadata.
        content = self._content
        if not self._has_metadata():
            self._content = (
                content + f"\n{METADATA_BEGIN}\n{metadata_yaml}{METADATA_END}\n"
            )
        else:
            metadata_start, metadata_end = self._metadata_indices()
            self._content = (
                content[: metadata_start + len(METADATA_BEGIN)]
                + "\n"
                + metadata_yaml
                + content[metadata_end:]
            )

    async def refresh(self):
        """Validate structure, run generators, update metadata"""

        await self._clear_cache()
        await self._load()
        await self._run_generators()
        self._update_metadata()
        # self._validate_structure()
        await self._save()

    def _validate_structure(self):
        """Validate page structure"""
        try:
            # Check for title
            if not self._title:
                raise PageValidationError(f"No title found in {self.path}")

            # Check for parent link.
            if not self._has_breadcrumb_parent():
                raise PageValidationError(f"No parent link found in {self.path}")

            # Validate metadata section.
            if not self._metadata:
                raise PageValidationError(f"No metadata in {self.path}")

        except Exception as e:
            print(self._content)
            raise PageValidationError(f"Validation failed for {self.path}: {e}")

    def _is_root_readme(self) -> bool:
        """Check if this is the root README.md"""
        return self.path == PrismPath("README.md")

    def _has_breadcrumb_parent(self) -> bool:
        """Check if page has a link to parent directory"""

        # Root readme has no parent link.
        if self._is_root_readme():
            return True

        # Root siblings only have the root readme.
        if self.path.parent == PrismPath():
            return "(README.md)" in self._content

        # Every other page should have a parent link.
        if "(../README.md)" in self._content:
            return True

        return False

    async def _run_generators(self):
        """Find and run all generators in the page asynchronously, serially."""

        async def replace_generator(match) -> str:
            """Run a generator and return the replaced string."""
            generator_type = match.group(1)
            try:
                generator = self._get_generator(generator_type)
                return (
                    f"<!-- prism:generate:{generator_type} -->\n"
                    f"{await generator.generate(self)}\n"
                    f"<!-- /prism:generate:{generator_type} -->"
                )
            except Exception as e:
                raise PageError(
                    f"Generator '{generator_type}' failed in {self.path}: {e}"
                )

        # Find all matches using re.finditer()
        matches = list(GENERATOR_PATTERN.finditer(self._content))
        if not matches:
            return

        # Process each match **sequentially** (serial execution)
        new_content = []
        last_pos = 0

        for match in matches:
            new_content.append(self._content[last_pos : match.start()])
            replacement = await replace_generator(match)
            new_content.append(replacement)
            last_pos = match.end()

        new_content.append(self._content[last_pos:])  # Append remaining content
        self._content = "".join(new_content)

    def _get_generator(self, generator_type: str) -> "Generator":
        """Get a generator instance by type"""
        generators = {
            "breadcrumbs": BreadcrumbsGenerator(),
            "pages": PagesGenerator(),
            "siblings": SiblingsGenerator(),
            "toc": TocGenerator(),
        }

        if generator_type not in generators:
            raise ValueError(f"Unknown generator type: {generator_type}")

        return generators[generator_type]

    def _find_generator_types(self) -> list[str]:
        """Find all generator types used in the page"""
        types = []
        pattern = r"<!--\s*prism:generate:(\w+)\s*-->"
        matches = re.finditer(pattern, self._content)
        for match in matches:
            types.append(match.group(1))
        return types
