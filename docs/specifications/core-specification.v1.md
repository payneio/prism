# Prism Core Specification v1

<!-- prism:generate:breadcrumbs -->
[Prism](../README.md) / [Specifications](README.md) / Prism Core Specification v1
<!-- /prism:generate:breadcrumbs -->

<!-- prism:generate:toc -->
- [Overview](#overview)
- [1. Data Model](#1-data-model)
  - [1.1 Node](#11-node)
    - [Node Structure (JSON Representation)](#node-structure-json-representation)
  - [1.2 Metadata Format](#12-metadata-format)
- [2. Directory Structure](#2-directory-structure)
  - [2.1 Special Files](#21-special-files)
- [3. Content Generators](#3-content-generators)
  - [3.1 Supported Generators](#31-supported-generators)
- [4. Indexing Mechanisms](#4-indexing-mechanisms)
  - [4.1 Backlink Index](#41-backlink-index)
  - [4.2 Tag Index](#42-tag-index)
  - [4.3 Search Index](#43-search-index)
- [5. Operations](#5-operations)
  - [5.1 Node Operations](#51-node-operations)
  - [5.2 Refresh Operation](#52-refresh-operation)
- [6. Projections](#6-projections)
- [7. Versioning and Compatibility](#7-versioning-and-compatibility)
- [8. Extensibility](#8-extensibility)
- [Conclusion](#conclusion)
<!-- /prism:generate:toc -->

## Overview

The Prism Core Specification defines the foundational structure, data formats, and operational rules that govern how content is managed within a Prism. This specification ensures interoperability across different implementations, whether accessed via command-line tools, libraries, APIs, or browser extensions.

## 1. Data Model

### 1.1 Node

A **Node** represents a discrete unit of content within a Prism. Nodes can be of the following types:

- **Page:** A Markdown (`.md`) file containing text, metadata, and optional dynamic content.
- **Folder:** A directory containing nodes, with a `README.md` serving as its index page.
- **Media:** Binary or text files (e.g., images, PDFs) associated with pages.

#### Node Structure (JSON Representation)

```json
{
  "id": "uuid-or-hash",
  "type": "page | folder | media",
  "path": "relative/path/to/node.md",
  "title": "Node Title",
  "content": "Markdown content",
  "metadata": {
    "created_at": "2025-02-09T12:00:00Z",
    "modified_at": "2025-02-09T15:30:00Z",
    "tags": ["knowledge", "AI"],
    "backlinks": ["../another-node.md"]
  },
  "links": {
    "internal": ["linked-page.md"],
    "external": ["https://external-link.com"],
    "media": ["image.png"]
  }
}
```

### 1.2 Metadata Format

Metadata is embedded in Markdown files using YAML front matter:

```yaml
---
title: "Prism Core Specification"
created_at: "2025-02-09T12:00:00Z"
tags: ["documentation", "spec"]
generator_types: ["toc", "backlinks"]
---
```

## 2. Directory Structure

A Prism’s content is organized in a hierarchical directory structure:

```
/prism-root
├── README.md
├── .prism/
│   ├── backlinks.txt
│   ├── tags.txt
│   └── .search
├── topics/
│   ├── README.md
│   └── topic1.md
└── media/
    └── image.png
```

### 2.1 Special Files

- **`README.md`**: Acts as an index page for directories.
- **`.prism/` Directory:** Stores system metadata:
  - `backlinks.txt` — Index of backlinks.
  - `tags.txt` — Global tag index.
  - `.search` — Search index file.

## 3. Content Generators

Content generators dynamically update sections of Markdown files. They are defined using special HTML comment blocks:

```markdown
<!-- prism:generate:toc -->
- [Overview](#overview)
- [1. Data Model](#1-data-model)
  - [1.1 Node](#11-node)
    - [Node Structure (JSON Representation)](#node-structure-json-representation)
  - [1.2 Metadata Format](#12-metadata-format)
- [2. Directory Structure](#2-directory-structure)
  - [2.1 Special Files](#21-special-files)
- [3. Content Generators](#3-content-generators)
  - [3.1 Supported Generators](#31-supported-generators)
- [4. Indexing Mechanisms](#4-indexing-mechanisms)
  - [4.1 Backlink Index](#41-backlink-index)
  - [4.2 Tag Index](#42-tag-index)
  - [4.3 Search Index](#43-search-index)
- [5. Operations](#5-operations)
  - [5.1 Node Operations](#51-node-operations)
  - [5.2 Refresh Operation](#52-refresh-operation)
- [6. Projections](#6-projections)
- [7. Versioning and Compatibility](#7-versioning-and-compatibility)
- [8. Extensibility](#8-extensibility)
- [Conclusion](#conclusion)
<!-- /prism:generate:toc -->
```

### 3.1 Supported Generators

- **Table of Contents (TOC):** Auto-generates a list of headings.
- **Backlinks:** Lists all pages linking to the current page.
- **Tags:** Displays tags associated with the page.
- **Projections:** Summarizes or restructures content based on specified rules.

## 4. Indexing Mechanisms

### 4.1 Backlink Index

Maintains a mapping of pages to their inbound links, stored in `backlinks.txt`:

```
page1.md: [page2.md, page3.md]
page2.md: [page4.md]
```

### 4.2 Tag Index

Tracks tags across the entire Prism, stored in `tags.txt`:

```
AI: [page1.md, page4.md]
knowledge: [page2.md]
```

### 4.3 Search Index

Supports full-text search and metadata queries, stored in `.search`.

## 5. Operations

### 5.1 Node Operations

- **Create:** Add new pages, folders, or media.
- **Update:** Modify content or metadata.
- **Move/Rename:** Change location or name, updating internal links.
- **Delete:** Remove nodes and clean up associated indexes.

### 5.2 Refresh Operation

Triggers validation and regeneration of dynamic content:

1. **Validate Structure:** Ensure links are valid, metadata exists.
2. **Run Generators:** Update dynamic content.
3. **Reindex:** Update backlinks, tags, and search indexes.

## 6. Projections

Projections create virtual views of content:

- **Sub-Prism:** Extracts a subtree of the Prism.
- **Flatten:** Combines multiple pages into a single Markdown document.
- **Summary:** Generates AI-assisted summaries of nodes and their relationships.

## 7. Versioning and Compatibility

Prism adheres to semantic versioning:

- **Major:** Breaking changes.
- **Minor:** New features, backward-compatible.
- **Patch:** Bug fixes, backward-compatible.

Backward compatibility is maintained through clear version markers in metadata:

```yaml
prism_version: "1.0.0"
```

## 8. Extensibility

Prism supports plugins for custom generators, sync mechanisms, and content processors. Extensions integrate via:

- API hooks
- Custom generator registration
- Protocol extensions

## Conclusion

This core specification serves as the foundation for all Prism implementations, ensuring consistent behavior, data integrity, and extensibility across platforms and use cases.

<!-- prism:metadata
---
title: Prism Core Specification v1
path: specifications/core-specification.v1.md
generator_types:
  - breadcrumbs
  - toc
  - toc
---
-->
