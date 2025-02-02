# Prism Documentation

<!-- prism:generate:toc -->
- [Prism](#prism)
- [Benefits](#benefits)
- [Core Features](#core-features)
- [Additional Documentation](#additional-documentation)
<!-- /prism:generate:toc -->

## Prism

Prism is a next-generation content management protocol designed for an
AI-enabled future. Prism lets you create, organize, and transform markdown-based
content with powerful projection and summarization capabilities.

Traditional content management systems weren't built for the AI age. Prism represents a new approach, where content isn't just stored and retrieved, but can be dynamically transformed, projected, and rewritten based on specific needs.

Think of Prism as a protocol more than a tool - it defines how content should be structured and linked to enable powerful transformations. While this implementation provides a CLI and Python library, the protocol is designed to be implemented across many tools and platforms.

## Benefits

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

## Core Features

- **Structured Wiki**: Create markdown-based wikis with guaranteed structural
  integrity
- **Content Generators**: Automatically generate and maintain tables of
  contents, sibling pages, directory listings, and more
- **Smart Projections**: Extract focused subsets of your content for specific
  purposes
- **AI-Powered Summarization**: Generate summaries from different perspectives,
  intelligently walking the content graph
- **Tag-Based Organization**: Flexible tagging system with automatic index
  maintenance
- **Command Line Interface**: Full control through a powerful CLI

## Additional Documentation

<!-- prism:generate:pages -->
- [Prism specification](SPEC.md)
- [Changelog](TODO.md)
<!-- /prism:generate:pages -->

<!-- prism:metadata
---
title: Prism Documentation
path: README.md
generator_types:
  - toc
  - pages
---
-->
