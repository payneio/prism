# Prism Indexing Specification v0

<!-- prism:generate:breadcrumbs -->
[Prism](../README.md) / [Specifications](README.md) / Prism Indexing Specification v0
<!-- /prism:generate:breadcrumbs -->

## Overview

The **Prism Indexing System** ensures efficient navigation, retrieval, and organization of content within a prism. It maintains backlinks, tag indexes, and full-text search capabilities, allowing for dynamic querying and content discovery.

## 1. Indexing Components

Prism maintains several types of indexes to enhance content management:

1. **Backlink Index**  
   - Tracks inbound links to a page from other pages in the prism.  
   - Supports reverse navigation and graph-based exploration.  

2. **Tag Index**  
   - Stores associations between tags and nodes.  
   - Enables efficient retrieval of all pages under a given tag.  

3. **Search Index**  
   - Provides full-text search across markdown content.  
   - Supports ranking and contextual snippets.  

4. **Metadata Index**  
   - Stores structured metadata for each node, allowing for rapid filtering.  

## 2. Data Model

### 2.1 Backlink Index (`backlinks.txt`)

Each prism maintains a global backlinks index stored as a simple key-value mapping.

**Format:**

```
[node_path] -> [list_of_referring_nodes]
```

**Example:**

```
docs/page-a.md -> ["docs/page-b.md", "docs/page-c.md"]
docs/page-b.md -> ["docs/page-d.md"]
```

### 2.2 Tag Index (`tags.txt`)

Stores a map of tags to associated nodes.

**Format:**

```
[tag] -> [list_of_nodes]
```

**Example:**

```
AI -> ["docs/page-a.md", "docs/page-c.md"]
Knowledge -> ["docs/page-b.md"]
```

### 2.3 Search Index (`.search/index.json`)

Stores precomputed search tokens for efficient retrieval.

**Example:**

```json
{
  "terms": {
    "knowledge": ["docs/page-a.md", "docs/page-b.md"],
    "ai": ["docs/page-a.md", "docs/page-c.md"]
  }
}
```

### 2.4 Metadata Index (`.prism/metadata.json`)

Tracks structured metadata for fast lookup.

**Example:**

```json
{
  "docs/page-a.md": {
    "created_at": "2025-02-09T12:00:00Z",
    "modified_at": "2025-02-09T15:30:00Z",
    "tags": ["AI", "research"]
  }
}
```

## 3. Indexing Operations

### 3.1 Backlink Indexing

Triggered when a page is:

- Created
- Updated (if links change)
- Deleted (removes references from other nodes)

Process:

1. Parse markdown to extract internal links.
2. Update `backlinks.txt` accordingly.

### 3.2 Tag Indexing

Triggered when:

- A tag is added/removed from a page.
- A page is deleted (removes it from tag lists).

Process:

1. Extract `tags` from metadata.
2. Update `tags.txt`.

### 3.3 Search Indexing

Triggered on:

- Page creation or modification.

Process:

1. Tokenize markdown content.
2. Store tokens in `.search/index.json`.

### 3.4 Metadata Indexing

Triggered on:

- Any metadata change (title update, timestamp, etc.).

Process:

1. Extract metadata from page.
2. Store/update in `.prism/metadata.json`.

## 4. Querying Indexes

### 4.1 Fetch Backlinks

```json
GET /index/backlinks?node=docs/page-a.md
```

**Response:**

```json
{
  "backlinks": ["docs/page-b.md", "docs/page-c.md"]
}
```

### 4.2 Retrieve Tag Index

```json
GET /index/tags?tag=AI
```

**Response:**

```json
{
  "nodes": ["docs/page-a.md", "docs/page-c.md"]
}
```

### 4.3 Search Query

```json
GET /search?q=knowledge
```

**Response:**

```json
{
  "results": [
    {
      "node": "docs/page-a.md",
      "snippet": "Knowledge management in AI systems..."
    }
  ]
}
```

## 5. Storage & Performance Considerations

- **Index Caching:** Reduce file system reads by keeping in-memory indexes.
- **Incremental Updates:** Modify only affected portions of the index.
- **Asynchronous Processing:** Non-blocking updates for performance.

---

This covers the **Indexing Specification** in a structured way. Would you like to refine any particular section or move on to another document?

<!-- prism:metadata
---
title: Prism Indexing Specification v0
path: specifications/indexing-specification.v0.md
generator_types:
  - breadcrumbs
---
-->
