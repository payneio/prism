# Changelog

<!-- prism:generate:breadcrumbs -->
[Prism](README.md) / Changelog
<!-- /prism:generate:breadcrumbs -->

- 2025-02-09:
  - Fixed some generator bugs in TOC and pages.
  - Added lots of docs.
- 2025-02-08:
  - Introduced asynchronous FileSystem interfaces with in-memory and local drive implementations.
  - User PrismPaths and asynchronous operations consistently throughout the library.
- 2025-02-02:
  - Change .prism file to a .prism directory. Put backlinks.txt and tags.txt and .search in it.
  - Update templates to have generators.
  - Change create page params to start with filename, make it or the title
  mandatory, and allow filenames to be specified without the .md extension (and
  .md will be added if necessary).

<!-- prism:metadata
---
title: Changelog
path: changelog.md
generator_types:
  - breadcrumbs
---
-->
