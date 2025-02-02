# src/prism/core/page.py
from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING
import re
from markdown.core import Markdown
import yaml
from ..exceptions import PrismError
from ..generators.toc import TocGenerator
from ..generators.pages import PagesGenerator
from ..generators.subdirs import SubdirsGenerator
from ..generators.siblings import SiblingsGenerator
from ..generators.breadcrumbs import BreadcrumbsGenerator

if TYPE_CHECKING:
    from ..prism import Prism
    from ..generators.base import Generator


class PageError(PrismError):
    """Base class for page-related errors"""

    pass


class PageValidationError(PageError):
    """Raised when page structure validation fails"""

    pass


METADATA_BEGIN = "<!-- prism:metadata\n---"
METADATA_END = "---\n-->"


class Page:
    """Represents a single page in a Prism repository"""

    GENERATOR_PATTERN = re.compile(
        r"<!--\s*prism:generate:(\w+)\s*-->(.*?)<!--\s*/prism:generate:\1\s*-->",
        re.DOTALL,
    )

    def __init__(self, prism: "Prism", path: Path):
        self.prism = prism
        self.path = path
        self._content: Optional[str] = None
        self._metadata: Optional[Dict[str, Any]] = None
        self._title: Optional[str] = None

    @property
    def content(self) -> str:
        """Get page content, loading from disk if needed"""
        if self._content is None:
            self._content = self.path.read_text(encoding="utf-8")
        return self._content

    @property
    def title(self) -> str:
        """Get the page title (first h1)"""
        if self._title is None:
            match = re.search(r"^#\s+(.+)$", self.content, re.MULTILINE)
            if not match:
                raise PageValidationError(f"No title (h1) found in {self.path}")
            self._title = match.group(1).strip()
        return self._title

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get page metadata, parsing if needed"""
        if self._metadata is None:
            self._metadata = self._parse_metadata()
        return self._metadata

    def _metadata_indices(self) -> tuple[int, int]:
        # Grab all content between <!-- prism:metadata --> markers.

        metadata_start = self.content.find(METADATA_BEGIN)
        metadata_end = self.content.find(METADATA_END)
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
        metadata_copy = self.content[
            metadata_start + len(METADATA_BEGIN) : metadata_end
        ].strip()
        try:
            return yaml.safe_load(metadata_copy)
        except yaml.YAMLError as e:
            raise PageError(f"Invalid metadata YAML in {self.path}: {e}")

    def refresh(self):
        """Validate structure, run generators, update metadata"""
        self._run_generators()
        self._update_metadata()
        # self._validate_structure()
        self._save()

    def _validate_structure(self):
        """Validate page structure"""
        try:
            # Check for title
            _ = self.title

            # Check for parent link.
            if not self._is_root_readme() and not self._has_parent_link():
                raise PageValidationError(f"No parent link found in {self.path}")

            # Validate metadata section.
            if not self.metadata:  # If metadata exists, check structure
                raise PageValidationError(f"No metadata in {self.path}")

        except Exception as e:
            raise PageValidationError(f"Validation failed for {self.path}: {e}")

    def _is_root_readme(self) -> bool:
        """Check if this is the root README.md"""
        return self.path.name == "README.md" and self.path.parent == self.prism.root

    def _has_parent_link(self) -> bool:
        """Check if page has a link to parent directory"""
        current_dir = self.path.parent

        # Root-level files don't need parent links
        if current_dir == self.prism.root:
            return True

        # - Relative: [Parent](../README.md)
        if "(../README.md)" in self.content:
            return True

        return False

    def _run_generators(self):
        """Find and run all generators in the page"""

        def replace_generator(match) -> str:
            generator_type = match.group(1)
            try:
                generator = self._get_generator(generator_type)
                # Keep the generator tags but put the generated content between them
                return (
                    f"<!-- prism:generate:{generator_type} -->\n"
                    f"{generator.generate(self)}\n"
                    f"<!-- /prism:generate:{generator_type} -->"
                )
            except Exception as e:
                raise PageError(
                    f"Generator '{generator_type}' failed in {self.path}: {e}"
                )

        self._content = self.GENERATOR_PATTERN.sub(replace_generator, self.content)

    def _get_generator(self, generator_type: str) -> "Generator":
        """Get a generator instance by type"""
        generators = {
            "breadcrumbs": BreadcrumbsGenerator(),
            "pages": PagesGenerator(),
            "siblings": SiblingsGenerator(),
            "subdirs": SubdirsGenerator(),
            "toc": TocGenerator(),
        }

        if generator_type not in generators:
            raise ValueError(f"Unknown generator type: {generator_type}")

        return generators[generator_type]

    def _update_metadata(self):
        """Update page metadata"""
        current_metadata = self.metadata.copy()

        # Update standard metadata fields
        current_metadata.update(
            {
                "title": self.title,
                "path": str(self.path.relative_to(self.prism.root)),
                "generator_types": self._find_generator_types(),
            }
        )

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

        # Update content with new metadata
        if not self._has_metadata():
            self._content = (
                self.content + f"\n{METADATA_BEGIN}\n{metadata_yaml}{METADATA_END}\n"
            )
        else:
            metadata_start, metadata_end = self._metadata_indices()
            self._content = (
                self.content[: metadata_start + len(METADATA_BEGIN)]
                + "\n"
                + metadata_yaml
                + self.content[metadata_end:]
            )

    def _find_generator_types(self) -> list[str]:
        """Find all generator types used in the page"""
        types = []
        pattern = r"<!--\s*prism:generate:(\w+)\s*-->"
        matches = re.finditer(pattern, self.content)
        for match in matches:
            types.append(match.group(1))
        return types

    def _save(self):
        """Save changes back to disk"""
        if self._content is not None:
            self.path.write_text(self._content, encoding="utf-8")
            self._content = None  # Reset cache
