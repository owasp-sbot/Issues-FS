# Issues-FS

[![PyPI version](https://badge.fury.io/py/issues-fs.svg)](https://pypi.org/project/issues-fs/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A file-system based issue tracking library with hierarchical structure and pluggable storage backends.**

Issues-FS stores issues as JSON files in a folder structure, enabling version control with Git, offline access, and flexible deployment options. It provides the core data layer for building issue tracking applications.

## Key Features

- **File-Based Storage** — Issues stored as `issue.json` files, easily version-controlled with Git
- **Hierarchical Structure** — Nest issues inside other issues via `issues/` subfolders
- **Pluggable Backends** — Works with memory, local disk, S3, SQLite, or ZIP via Memory-FS
- **MGraph-DB Integration** — Efficient graph queries for visualization and traversal
- **Type-Safe** — Built with `osbot-utils` Type_Safe patterns for runtime validation
- **Recursive Discovery** — Find issues at any depth in the hierarchy

## Installation

```bash
pip install issues-fs
```

## Quick Start

```python
from memory_fs.Memory_FS                          import Memory_FS
from memory_fs.storage_fs.Storage_FS__Memory      import Storage_FS__Memory
from memory_fs.storage_fs.Storage_FS__Local_Disk  import Storage_FS__Local_Disk
from issues_fs.graph.Graph__Repository            import Graph__Repository
from issues_fs.graph.Node__Service                import Node__Service
from issues_fs.graph.Type__Service                import Type__Service
from issues_fs.storage.Path__Handler__Graph_Node  import Path__Handler__Graph_Node

# Setup with in-memory storage (great for testing)
storage_fs   = Storage_FS__Memory()
memory_fs    = Memory_FS(storage_fs=storage_fs)
path_handler = Path__Handler__Graph_Node(base_path='')
repository   = Graph__Repository(memory_fs=memory_fs, path_handler=path_handler)

# Or use local disk storage
storage_fs   = Storage_FS__Local_Disk(root_path='.issues')
memory_fs    = Memory_FS(storage_fs=storage_fs)
path_handler = Path__Handler__Graph_Node(base_path='')
repository   = Graph__Repository(memory_fs=memory_fs, path_handler=path_handler)

# Initialize services
type_service = Type__Service(repository=repository)
node_service = Node__Service(repository=repository)

# Initialize default types
type_service.initialize_default_types()
```

## Core Operations

### Create an Issue

```python
from issues_fs.schemas.Schema__Node__Create__Request import Schema__Node__Create__Request

request = Schema__Node__Create__Request(
    node_type   = 'task',
    title       = 'Implement user authentication',
    description = 'Add OAuth2 support',
    status      = 'backlog',
    tags        = ['security', 'backend']
)

response = node_service.create_node(request)

if response.success:
    print(f"Created: {response.node.label}")  # Task-1
```

### Load an Issue

```python
from issues_fs.schemas.Safe_Str__Graph_Types import Safe_Str__Node_Type, Safe_Str__Node_Label

node = repository.node_load(
    node_type = Safe_Str__Node_Type('task'),
    label     = Safe_Str__Node_Label('Task-1')
)

print(node.title)   # "Implement user authentication"
print(node.status)  # "backlog"
```

### Find All Issues (Recursive)

```python
# Find all issues, including nested ones
all_nodes = repository.nodes_list_all()

for info in all_nodes:
    print(f"{info.label} ({info.node_type}) at {info.path}")

# Filter by root path
project_nodes = repository.nodes_list_all(
    root_path=Safe_Str__File__Path('data/project/Project-1')
)
```

### Load by Path

```python
# Load issue by folder path
node = repository.node_load_by_path(
    Safe_Str__File__Path('data/project/Project-1/issues/Version-1/issues/Task-1')
)

# Find path for a label
path = repository.node_find_path_by_label(Safe_Str__Node_Label('Task-1'))
```

### Update an Issue

```python
from issues_fs.schemas.Schema__Node__Update__Request import Schema__Node__Update__Request

request = Schema__Node__Update__Request(
    status = 'in-progress',
    tags   = ['security', 'backend', 'urgent']
)

response = node_service.update_node(
    node_type = Safe_Str__Node_Type('task'),
    label     = Safe_Str__Node_Label('Task-1'),
    request   = request
)
```

### Delete an Issue

```python
response = node_service.delete_node(
    node_type = Safe_Str__Node_Type('task'),
    label     = Safe_Str__Node_Label('Task-1')
)
```

## MGraph-DB Integration

For efficient graph queries and visualization:

```python
from issues_fs.mgraph.MGraph__Issues__Sync__Service import MGraph__Issues__Sync__Service
from issues_fs.mgraph.MGraph__Issues__Domain        import MGraph__Issues__Domain

# Create sync service
sync_service = MGraph__Issues__Sync__Service(
    repository   = repository,
    path_handler = path_handler
)

# Lazy load graph (syncs from filesystem)
graph = sync_service.ensure_loaded()

# Query by label
node = graph.get_node_by_label('Task-1')

# Get children
children = graph.get_children(node.node_id)

# Get ancestors (path to root)
ancestors = graph.get_ancestors(node.node_id)

# Force resync after external changes
sync_service.full_sync()
```

## Storage Structure

Issues-FS uses a simple, human-readable folder structure:

```
.issues/
├── config/
│   ├── node-types.json          # Issue type definitions
│   └── link-types.json          # Link type definitions
├── data/
│   └── {type}/
│       └── {Label}/
│           ├── issue.json       # Issue data
│           └── issues/          # Child issues
│               └── {Child-Label}/
│                   └── issue.json
└── indexes/
    └── issues.mgraph.json       # MGraph-DB cache
```

### Example Structure

```
.issues/
├── data/
│   └── project/
│       └── Project-1/
│           ├── issue.json
│           └── issues/
│               ├── Version-1/
│               │   ├── issue.json
│               │   └── issues/
│               │       ├── Task-1/
│               │       │   └── issue.json
│               │       └── Bug-2/
│               │           └── issue.json
│               └── Version-2/
│                   └── issue.json
```

## Issue JSON Schema

```json
{
  "node_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "node_type": "task",
  "node_index": 1,
  "label": "Task-1",
  "title": "Implement user authentication",
  "description": "Add OAuth2 support for user login",
  "status": "in-progress",
  "created_at": 1706745600000,
  "updated_at": 1706832000000,
  "tags": ["security", "backend"],
  "links": [
    {
      "verb": "blocks",
      "target_label": "Task-2"
    }
  ],
  "properties": {
    "priority": "high",
    "estimate": "3d"
  }
}
```

## Node Types

Default node types are created on initialization:

```python
type_service.initialize_default_types()
```

```json
{
  "types": [
    {"name": "git-repo", "display_name": "Git Repo", "color": "#6e5494", "default_status": "active"},
    {"name": "project", "display_name": "Project", "color": "#4A90D9", "default_status": "active"},
    {"name": "version", "display_name": "Version", "color": "#7B68EE", "default_status": "planned"},
    {"name": "task", "display_name": "Task", "color": "#50C878", "default_status": "backlog"},
    {"name": "bug", "display_name": "Bug", "color": "#FF6B6B", "default_status": "open"},
    {"name": "feature", "display_name": "Feature", "color": "#FFD700", "default_status": "backlog"},
    {"name": "user-story", "display_name": "User Story", "color": "#20B2AA", "default_status": "backlog"}
  ]
}
```

### Custom Types

```python
from issues_fs.schemas.Schema__Node__Type import Schema__Node__Type

custom_type = Schema__Node__Type(
    name           = 'epic',
    display_name   = 'Epic',
    color          = '#9B59B6',
    icon           = 'rocket',
    statuses       = ['draft', 'active', 'completed'],
    default_status = 'draft'
)

type_service.create_node_type(custom_type)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Services                              │
│       Node__Service  │  Type__Service  │  Link__Service      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    Graph__Repository                         │
│            (Data access layer with Type_Safe)                │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                        Memory-FS                             │
│     Storage_FS__Memory │ Storage_FS__Local_Disk │ S3 │ ...  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    MGraph Integration                        │
│  MGraph__Issues__Sync__Service  →  MGraph__Issues__Domain   │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `Graph__Repository` | Data access layer for nodes, types, indexes |
| `Node__Service` | Business logic for CRUD operations |
| `Type__Service` | Manage node and link type definitions |
| `Link__Service` | Manage links between issues |
| `MGraph__Issues__Sync__Service` | Syncs filesystem to MGraph-DB |
| `MGraph__Issues__Domain` | Graph operations and indexes |
| `Path__Handler__Graph_Node` | Generate filesystem paths |

## Development

### Setup

```bash
git clone https://github.com/owasp-sbot/Issues-FS.git
cd Issues-FS
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Style

This project follows the [OSBot Python Formatting Guide](https://github.com/owasp-sbot/OSBot-Utils):

- Type_Safe inheritance on all classes
- Safe_* primitives for type validation
- `@type_safe` decorator on public methods
- Aligned imports/parameters at column 70-80
- Explicit `is True` / `is False` for booleans

## Dependencies

- [Memory-FS](https://github.com/owasp-sbot/Memory-FS) — Pluggable filesystem abstraction
- [MGraph-DB](https://github.com/owasp-sbot/MGraph-DB) — Graph database operations
- [OSBot-Utils](https://github.com/owasp-sbot/OSBot-Utils) — Type_Safe utilities

## Use Cases

- **Git-native issue tracking** — Store issues alongside code, branch/merge with PRs
- **Offline-first workflows** — Full functionality without network access
- **Custom integrations** — Simple JSON format for easy tooling
- **Hierarchical project management** — Organize epics → features → tasks → subtasks
- **Embedded issue tracking** — Add issue tracking to any Python application

## License

MIT License — see [LICENSE](LICENSE) for details.