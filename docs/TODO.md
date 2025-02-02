# Changelog

<!-- prism:generate:breadcrumbs -->
[Prism Documentation](README.md) > Changelog
<!-- /prism:generate:breadcrumbs -->

## Upcoming

These items are generally in order of what will be delivered next.

- **Move page**: Make page move work.
- **Move folder**: Make page move work.
- **Back indexes**: Maintain back indexes for navigation.
- **Flatten**: Make a part of a prism a single md page. `prism flatten <page> --depth=2`
- **Re-root**: Make a given page the new root of a prism repo and restructure the entire thing.
- **Client working directory**: When using prism, it should work from your current dir, not the root.
- **Subprism prevention**: Prevent a prism from being created inside a prism. Maybe?

## Done

- 20205-02-02:
  - Change .prism file to a .prism directory. Put backlinks.txt and tags.txt and .search in it.
  - Update templates to have generators.
  - Change create page params to start with filename, make it or the title
  mandatory, and allow filenames to be specified without the .md extension (and
  .md will be added if necessary).

<!-- prism:metadata
---
title: Changelog
path: TODO.md
generator_types:
  - breadcrumbs
---
-->
