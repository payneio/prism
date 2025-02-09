# src/prism/generators/base.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..page import Page


class Generator(ABC):
    """Base class for all generators"""

    @abstractmethod
    async def generate(self, page: "Page") -> str:
        """Generate content for the given page"""
        pass
