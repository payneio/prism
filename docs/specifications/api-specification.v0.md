# Prism API Specification v0

<!-- prism:generate:breadcrumbs -->
[Prism](../README.md) / [Specifications](README.md) / Prism API Specification v0
<!-- /prism:generate:breadcrumbs -->

## Overview

The Prism API Specification defines the endpoints, request/response formats, and operational guidelines for interacting with Prism data programmatically. This API facilitates content management, indexing, synchronization, and dynamic content generation across various clients, including CLI tools, browser extensions, and third-party applications.

## 1. API Design Principles

- **RESTful Architecture:** Follows REST principles for simplicity and scalability.
- **JSON for Data Exchange:** Uses JSON for request and response payloads.
- **Stateless Operations:** Each request contains all necessary information, ensuring no dependency on server-side sessions.
- **Versioning:** API versioning is embedded in the URL (e.g., `/api/v1/`).

## 2. Authentication & Authorization

- **Token-Based Authentication:** Supports JWT (JSON Web Tokens) for secure access.
- **Role-Based Access Control (RBAC):** Manages permissions for different user roles (admin, editor, viewer).

## 3. Endpoint Structure

### 3.1 Base URL

```
https://{host}/api/v1/
```

### 3.2 Endpoints Overview

- **Nodes:** `/nodes`
- **Prisms:** `/prisms`
- **Generators:** `/generators`
- **Sync:** `/sync`
- **Search:** `/search`

## 4. Node Operations

### 4.1 Create Node

- **POST** `/nodes`

**Request Body:**

```json
{
  "type": "page",
  "title": "New Page",
  "path": "docs/new-page.md",
  "content": "# Heading\nContent goes here.",
  "metadata": {
    "tags": ["example", "api"]
  }
}
```

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "created"
}
```

### 4.2 Get Node

- **GET** `/nodes/{id}`

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "New Page",
  "content": "# Heading\nContent goes here.",
  "metadata": {
    "tags": ["example", "api"],
    "created_at": "2025-02-09T12:00:00Z",
    "modified_at": "2025-02-09T15:30:00Z"
  }
}
```

### 4.3 Update Node

- **PUT** `/nodes/{id}`

**Request Body:**

```json
{
  "title": "Updated Page Title",
  "content": "# Updated Content",
  "metadata": {
    "tags": ["updated", "api"]
  }
}
```

**Response:**

```json
{
  "status": "updated",
  "modified_at": "2025-02-09T16:00:00Z"
}
```

### 4.4 Delete Node

- **DELETE** `/nodes/{id}`

**Response:**

```json
{
  "status": "deleted"
}
```

## 5. Prism Operations

### 5.1 Create Prism

- **POST** `/prisms`

**Request Body:**

```json
{
  "name": "My New Prism",
  "root_path": "/prisms/my-new-prism"
}
```

**Response:**

```json
{
  "id": "prism-12345",
  "status": "created"
}
```

### 5.2 Refresh Prism

- **PATCH** `/prisms/{id}/refresh`

**Response:**

```json
{
  "status": "refreshed",
  "updated_indexes": ["backlinks", "tags", "search"]
}
```

## 6. Generator Operations

### 6.1 Run Generator

- **POST** `/generators/run`

**Request Body:**

```json
{
  "type": "toc",
  "node_id": "123e4567-e89b-12d3-a456-426614174000",
  "config": {
    "depth": 2
  }
}
```

**Response:**

```json
{
  "output": "- [Heading 1](#heading-1)\n  - [Subheading](#subheading)"
}
```

## 7. Sync Operations

### 7.1 Start Sync

- **POST** `/sync/start`

**Request Body:**

```json
{
  "method": "sftp",
  "remote_url": "sftp://example.com/prism"
}
```

**Response:**

```json
{
  "status": "sync_in_progress"
}
```

### 7.2 Get Sync Status

- **GET** `/sync/status`

**Response:**

```json
{
  "status": "completed",
  "last_synced_at": "2025-02-09T16:00:00Z"
}
```

## 8. Search Operations

### 8.1 Full-Text Search

- **GET** `/search?q=example`

**Response:**

```json
{
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Example Page",
      "snippet": "This is an example content snippet..."
    }
  ]
}
```

## 9. Error Handling

Standardized error responses:

```json
{
  "error": {
    "code": "404",
    "message": "Resource not found",
    "details": "The requested node ID does not exist."
  }
}

```

## 10. Versioning

API versions are included in the URL (e.g., `/api/v1/`). Changes are categorized as:

- **Major:** Breaking changes.
- **Minor:** New features, backward-compatible.
- **Patch:** Bug fixes, backward-compatible.

## Conclusion

This API specification ensures consistent, secure, and scalable interaction with Prism data, supporting a range of applications and integrations.

<!-- prism:metadata
---
title: Prism API Specification v0
path: specifications/api-specification.v0.md
generator_types:
  - breadcrumbs
---
-->
