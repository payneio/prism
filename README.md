# Prism

A next-generation content management protocol designed for an AI-enabled future. Prism lets you create, organize, and transform markdown-based content with powerful projection and summarization capabilities.

[Documentation](docs/README.md)

## Core Features

- **Structured Wiki**: Create markdown-based wikis with guaranteed structural integrity
- **Content Generators**: Automatically generate and maintain tables of contents, sibling pages, directory listings, and more
- **Smart Projections**: Extract focused subsets of your content for specific purposes
- **AI-Powered Summarization**: Generate summaries from different perspectives, intelligently walking the content graph
- **Tag-Based Organization**: Flexible tagging system with automatic index maintenance
- **Command Line Interface**: Full control through a powerful CLI

## Quick Start

```bash
# Install Prism
pip install prism

# OR, if you're in dev:
uv pip install -e .

# Initialize a new Prism wiki
prism init my-wiki

# Add some content
cd my-wiki
prism page add "Getting Started"
```

## Example Page

```markdown
# Project Overview

<!-- prism:generate:toc -->
<!-- /prism:generate:toc -->

Content here...

## Related Pages
<!-- prism:generate:siblings -->
<!-- /prism:generate:siblings -->

## Subdirectories
<!-- prism:generate:subdirs -->
<!-- /prism:generate:subdirs -->
```

## Key Commands

```bash
# Add content
prism page add "Page Title"
prism folder add project/docs

# Update content
prism page refresh README.md
prism folder refresh docs --recurse

# Transform content
prism project README.md --depth 2
prism summarize docs/architecture.md "security implications"
```

## Development

Prism uses Python 3.10+ and uv for dependency management.

```bash
# Set up development environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install uv
uv pip install -e .
```

## Why Prism?

Traditional content management systems weren't built for the AI age. Prism represents a new approach, where content isn't just stored and retrieved, but can be dynamically transformed, projected, and rewritten based on specific needs.

Think of Prism as a protocol more than a tool - it defines how content should be structured and linked to enable powerful transformations. While this implementation provides a CLI and Python library, the protocol is designed to be implemented across many tools and platforms.

## License

MIT
