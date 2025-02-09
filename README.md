# Prism

A next-generation content management protocol designed for an AI-enabled future. Prism lets you create, organize, and transform markdown-based content with powerful projection and summarization capabilities.

[Documentation](docs/README.md)

## Quick Start

### Command line client

```bash
# Install Prism command line client.
pip install prism # Doesn't work, yet.

# OR, if you're developing locally:
uv pip install -e .

# Help.
prism --help

# Initialize a new Prism repo.
prism init my-wiki

# Add some content.
cd my-wiki
prism page add getting_started.md "Getting Started"

prism folder add docs
cd folder
prism page add hello.md "Hello!"

# Validate and rebuild all prism structure throughout the repo.
prism refresh
```

## Development

Prism uses Python 3.10+ and uv for dependency management.

```bash
# Set up development environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install uv

uv sync --all-extras
uv pip install -e .
```

## License

MIT
