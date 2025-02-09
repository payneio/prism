# Prism Core Specification v0

<!-- prism:generate:breadcrumbs -->
[Prism](../README.md) / [Specifications](README.md) / Prism Core Specification v0
<!-- /prism:generate:breadcrumbs -->

<!-- prism:generate:toc -->
- [Overview](#overview)
  - [Benefits](#benefits)
- [Library capabilities](#library-capabilities)
- [Command line client](#command-line-client)
  - [Editor features](#editor-features)
- [Components](#components)
  - [Refresh](#refresh)
- [Implementation notes](#implementation-notes)
  - [Source code layout](#source-code-layout)
<!-- /prism:generate:toc -->

## Overview

This is a general project specification currently. It will be broken apart as
the project takes shape.

This page considers the design of a piece of software to make content management
more powerful for individuals and organizations. The main idea is to have a
text-based wiki that makes it quick for organizing thought and information
towards a specific purpose. It is not intended to be a general knowledge store
(though it might be able to be used as such). Instead, it imagines a future
where a topic is explored in depth in a structured way.

### Benefits

- An AI assistant can build a purpose-built prism on your behalf or in
  collaboration with you.
- You can snapshot/fork/project/a prism to provide context to an AI assistant.
- Many systems can interface with a powerful general-purpose text-based content
  management system.
- Markdown is ubiquitous and simple.
- A prism acts as a knowledge graph/graph db, so it can be used to create
  projections/sub-graphs.
- An idea like this has been useful in the past, but required power-users
  (librarians) to really maintain them. Now that LLMs are everywhere, though,
  this system can be used as the backend to an LLM assistant giving it
  exceptional context-management capabilities. Context can be searched and
  assembled (projected/summarized) on the fly.
- Git-friendly (good for openness).
- Editor agnostic. Reader agnostic (may consider creating mobile clients).

## Library capabilities

- Allows for structural editing (viewing and editing will be in editor of
  choice, e.g. VS Code).
- Maintains item (directory/page/media) structure.
  - Every page has a title. Page filename is a version of the title.
  - Every page has a metadata section at the bottom.
  - Breadcrumb: Every page has a backlink to it's parent directory.
  - Every folder has a README.md.
  - Every README has a "Pages TOC"
  - All internal links work.
- Maintains prism structure
  - People in `/people`.
  - Organizations in `/organizations`.
- Maintains media structure.
  - Media can be added to any page. `<page_path>/<media_filename>`.
  - All media will have metadata next to it `<page_path>/<media_filename>.metadata`
- Maintains backlink index (`backlinks.txt`).
- Maintains tag index (`tags.txt`).
- Maintains search index.
- Generators: populate sections of a page using html comments as directives, e.g.:
  - <!\-- prism:generate:toc -->, breadcrumbs, tagged:pinned, siblings, children, etc.
- Allows for projections of prism (creating a sub-prism, flattening a part of a
  prism, or a creating a summary of a node and it's subnodes).
- Allows for LLM-driven refactoring: merging pages, splitting pages, or even
  reorganization of entire sections using natural language.

## Command line client

- `prism page`
  - `prism page add <title>`. Add a page. Link to parent folder README.md. backlink.
  - `prism page rename <old> <new>`. Update links.
  - `prism page move <old> <new>`. Update links.
  - `prism page delete <page>`
  - `prism page refresh <page>`. Validates page structure, runs generators,
    updates metadata, indexes the page for search, etc.
  - `prism page links <page> --internal --external --media`. Shows all links in a page.
  - `prism page backlinks <page>`. Shows all links to a page.
  - `prism page tag <page> <tag>`
  - `prism page untag <page> <tag>`
- `prism folder`
  - `prism folder add`. Add a folder. Create a README.md by default. Link to parent.
  - `prism folder rename <old> <new>`. Moves a folder and all its contents. Updates links in all subitems.
  - `prism folder move <old> <new>`.
  - `prism folder delete <folder>`. Deletes all subitems. Removes from index.
  - `prism folder refresh <folder> --recurse`. Refresh all pages in a folder.
  - `prism folder list <folder> --pages --folders --media --recurse`. Lists all subitems of a folder.
  - `prism folder tag <folder> <tag>`
  - `prism folder untag <folder> <tag>`
- `prism item` (a page or a folder or media)
    `prism delete <item_path>`
- `prism project <page> --depth --flatten`. Generate a new prism from a specific
  page to a given depth. Flatten into a single file if desired.
- `prism summarize <page> <perspective>`. Power feature--summarize a page from a
  certain perspective. This may +walk to associated pages to various depths and
  use LLMs to figure out what should be included in the summary. The summary
  will be an extensive .md file.
- More TBD.

### Editor features

For various editors, we might make plugins that can use the prism cli or library
to provide interactive utilities.

- Create a link using a hotkey. Uses name from page.
- Create a page and link here.
- Generate text/section using a hotkey.
- Insert media (selecting or pasting).

## Components

### Refresh

The main command for updating both content and metadata. It nicely encompasses both the structural validation and the content generation aspects.

Let's think through what a complete page refresh would do:

1. Structure Validation
   - Verify page has a title
   - Check that parent directory link exists and is valid
   - Validate all internal links
   - Verify media references point to valid files
   - Check metadata section exists and is properly formatted
2. Run Generators
   - Find all `<!-- prism:generate:X -->` blocks
   - Generate fresh content for each block
   - Replace content between opening/closing tags
   - Common generators might include:
     - Table of contents
     - List of sibling pages
     - List of children pages (links to subdirectory README.mds)
     - External references/links
     - Tag list
     - Backlinks
3. Update Metadata
   - Update/verify metadata section at bottom of page
   - Update search index
   - Update backlinks index
   - Update tags index

The recursive folder refresh is powerful - it would help maintain consistency across an entire section of the prism. Would be especially useful after moving pages around or making structural changes.

Would you like to explore the implementation details of any of these components? We could start with the generator system or the structure validation logic.

## Implementation notes

### Source code layout

```
prism/
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # Project documentation
├── docs/                       # Project documentation (it's a prism!)
├── src/
│   └── prism/
│       ├── __init__.py        # Package initialization
│       ├── prism.py           # Core Prism class
│       ├── config.py          # Configuration handling
│       ├── exceptions.py      # Custom exceptions
│       │
│       ├── cli/
│       │   ├── __init__.py    # Command line interface
│       │   ├── page.py        # Page subcommands
│       │   └── folder.py      # Folder subcommands
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── page.py        # Page class and operations
│       │   ├── folder.py      # Folder class and operations
│       │   └── media.py       # Media file handling
│       │
│       ├── generators/
│       │   ├── __init__.py
│       │   ├── base.py        # Base Generator class
│       │   ├── breadcrumbs.py # Breadcrumbs generator
│       │   ├── toc.py         # Table of Contents generator
│       │   ├── siblings.py    # Sibling pages generator
│       │   └── subdirs.py     # Subdirectories generator
│       │
│       ├── indices/
│       │   ├── __init__.py
│       │   ├── backlinks.py   # Backlinks index management
│       │   ├── tags.py        # Tags index management
│       │   └── search.py      # Search index management
│       │
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── markdown.py    # Markdown parsing utilities
│       │   └── metadata.py    # Metadata parsing/validation
│       │
│       └── utils/
│           ├── __init__.py
│           ├── fs.py          # Filesystem operations
│           ├── links.py       # Link validation/manipulation
│           └── paths.py       # Path handling utilities
│
├── tests/
│   ├── conftest.py           # Test configuration
│   ├── test_wiki.py
│   ├── test_config.py
│   │
│   ├── core/
│   │   ├── test_page.py
│   │   ├── test_folder.py
│   │   └── test_media.py
│   │
│   ├── generators/
│   │   ├── test_toc.py
│   │   ├── test_siblings.py
│   │   └── test_subdirs.py
│   │
│   ├── indices/
│   │   ├── test_backlinks.py
│   │   ├── test_tags.py
│   │   └── test_search.py
│   │
│   └── ... etc.
│
└── examples/
    ├── simple_wiki/          # Example wiki structure
    └── scripts/              # Example usage scripts
```

<!-- prism:metadata
---
title: Prism specification
path: SPEC.md
generator_types:
  - breadcrumbs
  - X
---
-->

<!-- prism:metadata
---
title: Prism specification
path: specifications/core-specification.v0.md
generator_types:
  - breadcrumbs
  - X
---
-->

<!-- prism:metadata
---
title: Prism Core Specification v0
path: specifications/core-specification.v0.md
generator_types:
  - breadcrumbs
  - X
---
-->

<!-- prism:metadata
---
title: Prism Core Specification v0
path: specifications/core-specification.v0.md
generator_types:
  - breadcrumbs
  - toc
  - X
---
-->
