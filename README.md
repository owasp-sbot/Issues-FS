# Issues-FS

[![PyPI version](https://badge.fury.io/py/issues-fs.svg)](https://pypi.org/project/issues-fs/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**A file-system-based, graph-oriented issue tracking library with hierarchical structure and pluggable storage backends.**

Issues-FS stores issues as JSON files in `.issues/` directories inside git repos, enabling version control with Git, offline access, and flexible deployment options. It provides the core data layer for building issue tracking applications -- both for human developers and AI agent workflows.

## Key Features

- **File-Based Storage** -- Issues stored as `issue.json` files, easily version-controlled with Git
- **Graph-Oriented Model** -- Issues, types, and links form a traversable graph via MGraph-DB integration
- **Hierarchical Structure** -- Nest issues inside other issues via `issues/` subfolders (projects > versions > tasks > subtasks)
- **Pluggable Backends** -- Works with memory, local disk, S3, SQLite, or ZIP via Memory-FS
- **Type-Safe** -- Built with `osbot-utils` Type_Safe patterns for runtime validation
- **Recursive Discovery** -- Find issues at any depth in the hierarchy
- **Human-Readable** -- Plain JSON files in a simple folder structure, inspectable with any text editor

## Installation

```bash
pip install issues-fs
```

For command-line usage, also install the CLI:

```bash
pip install issues-fs-cli
```

## Quick Start

```python
from memory_fs.Memory_FS                          import Memory_FS
from memory_fs.storage_fs.Storage_FS__Memory      import Storage_FS__Memory
from memory_fs.storage_fs.Storage_FS__Local_Disk  import Storage_FS__Local_Disk
from issues_fs.issues.graph_services.Graph__Repository  import Graph__Repository
from issues_fs.issues.graph_services.Node__Service      import Node__Service
from issues_fs.issues.graph_services.Type__Service      import Type__Service
from issues_fs.issues.storage.Path__Handler__Graph_Node import Path__Handler__Graph_Node

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
from issues_fs.schemas.graph.Schema__Node__Create__Request import Schema__Node__Create__Request

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
from issues_fs.schemas.safe_str.Safe_Str__Graph_Types import Safe_Str__Node_Type, Safe_Str__Node_Label

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
from issues_fs.schemas.graph.Schema__Node__Update__Request import Schema__Node__Update__Request

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
from issues_fs.mgraph.MGraph__Issues__Domain import MGraph__Issues__Domain

# Create sync service
from issues_fs.issues.graph_services.Graph__Repository__Factory import Graph__Repository__Factory

factory    = Graph__Repository__Factory(root_path='.issues')
repository = factory.create_repository()

# Query the graph
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

## CLI Usage

The [Issues-FS CLI](https://github.com/owasp-sbot/Issues-FS__CLI) provides command-line access to all operations:

```bash
# List all issues in the current repo
issues-fs list

# Create a new issue
issues-fs create --type task --title "Fix login bug"

# Show issue details
issues-fs show Task-1

# Update status
issues-fs update Task-1 --status in-progress
```

Install the CLI separately: `pip install issues-fs-cli`

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

| Type | Display Name | Default Status |
|------|-------------|----------------|
| `git-repo` | Git Repo | active |
| `project` | Project | active |
| `version` | Version | planned |
| `task` | Task | backlog |
| `bug` | Bug | open |
| `feature` | Feature | backlog |
| `user-story` | User Story | backlog |

### Custom Types

```python
from issues_fs.schemas.graph.Schema__Node__Type import Schema__Node__Type

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
┌──────────────────────────────────────────────────────────┐
│                       Services                           │
│      Node__Service  │  Type__Service  │  Link__Service   │
└───────────────────────────┬──────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────┐
│                   Graph__Repository                      │
│           (Data access layer with Type_Safe)             │
└───────────────────────────┬──────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────┐
│                       Memory-FS                          │
│    Storage_FS__Memory │ Storage_FS__Local_Disk │ S3 │ …  │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                   MGraph Integration                     │
│ MGraph__Issues__Sync__Service  →  MGraph__Issues__Domain │
└──────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `Graph__Repository` | Data access layer for nodes, types, indexes |
| `Graph__Repository__Factory` | Factory for creating configured repository instances |
| `Node__Service` | Business logic for CRUD operations |
| `Type__Service` | Manage node and link type definitions |
| `Link__Service` | Manage links between issues |
| `Comments__Service` | Manage comments on issues |
| `MGraph__Issues__Sync__Service` | Syncs filesystem to MGraph-DB |
| `MGraph__Issues__Domain` | Graph operations and indexes |
| `Path__Handler__Graph_Node` | Generate filesystem paths for graph nodes |
| `Path__Handler__Issues` | Generate filesystem paths for issue operations |

### Module Structure

```
issues_fs/
├── issues/
│   ├── graph_services/      # Core services (Repository, Node, Type, Link, Comments)
│   ├── storage/             # Path handlers for filesystem operations
│   ├── phase_1/             # Root issue and children services
│   └── status/              # Issue status management
├── mgraph/                  # MGraph-DB integration (domain model, sync, schemas)
├── schemas/                 # Data models and type definitions
│   ├── graph/               # Graph node schemas (create, update, delete)
│   ├── issues/              # Issue-specific schemas
│   ├── identifiers/         # ID types and generators
│   ├── safe_str/            # Type-safe string primitives
│   ├── enums/               # Enumeration types
│   └── status/              # Status-related schemas
├── scripts/                 # Utility scripts
├── utils/                   # Version info and utilities
└── version/                 # Package version management
```

## The Issues-FS Ecosystem

This library is the core of a broader ecosystem coordinated through [Issues-FS__Dev](https://github.com/owasp-sbot/Issues-FS__Dev), which includes a CLI, web service, documentation, and a team of 10 AI agent roles that collaborate through Issues-FS itself.

### Repository Map

#### Core Libraries

| Repository | Description |
|-----------|-------------|
| [Issues-FS](https://github.com/owasp-sbot/Issues-FS) | **This repo** -- core Python library |
| [Issues-FS__CLI](https://github.com/owasp-sbot/Issues-FS__CLI) | Command-line interface |
| [Issues-FS__Docs](https://github.com/owasp-sbot/Issues-FS__Docs) | Architecture documents, design briefs, specifications |

#### Services

| Repository | Description |
|-----------|-------------|
| [Issues-FS__Service](https://github.com/owasp-sbot/Issues-FS__Service) | FastAPI web service |
| [Issues-FS__Service__UI](https://github.com/owasp-sbot/Issues-FS__Service__UI) | Web UI |
| [Issues-FS__Service__Client__Python](https://github.com/owasp-sbot/Issues-FS__Service__Client__Python) | Python client for the service API |

#### Development

| Repository | Description |
|-----------|-------------|
| [Issues-FS__Dev](https://github.com/owasp-sbot/Issues-FS__Dev) | Parent orchestration repo for all submodules |

#### Agent Roles

| Repository | Description |
|-----------|-------------|
| [Issues-FS__Dev__Role__Dev](https://github.com/owasp-sbot/Issues-FS__Dev__Role__Dev) | Dev agent -- implementation |
| [Issues-FS__Dev__Role__Architect](https://github.com/owasp-sbot/Issues-FS__Dev__Role__Architect) | Architect agent -- system design |
| [Issues-FS__Dev__Role__QA](https://github.com/owasp-sbot/Issues-FS__Dev__Role__QA) | QA agent -- testing |
| [Issues-FS__Dev__Role__AppSec](https://github.com/owasp-sbot/Issues-FS__Dev__Role__AppSec) | AppSec agent -- security |
| [Issues-FS__Dev__Role__DevOps](https://github.com/owasp-sbot/Issues-FS__Dev__Role__DevOps) | DevOps agent -- CI/CD |
| [Issues-FS__Dev__Role__Librarian](https://github.com/owasp-sbot/Issues-FS__Dev__Role__Librarian) | Librarian agent -- knowledge connectivity |
| [Issues-FS__Dev__Role__Cartographer](https://github.com/owasp-sbot/Issues-FS__Dev__Role__Cartographer) | Cartographer agent -- system mapping |
| [Issues-FS__Dev__Role__Historian](https://github.com/owasp-sbot/Issues-FS__Dev__Role__Historian) | Historian agent -- project narrative |
| [Issues-FS__Dev__Role__Journalist](https://github.com/owasp-sbot/Issues-FS__Dev__Role__Journalist) | Journalist agent -- reporting |
| [Issues-FS__Dev__Role__Conductor](https://github.com/owasp-sbot/Issues-FS__Dev__Role__Conductor) | Conductor agent -- orchestration |

#### Human

| Repository | Description |
|-----------|-------------|
| [Issues-FS__Dev__Human__Dinis_Cruz](https://github.com/owasp-sbot/Issues-FS__Dev__Human__Dinis_Cruz) | Stakeholder repo for Dinis Cruz |

## Current Status

- **Version:** v0.4.5
- **Tests:** 475+ test methods across 36 test files
- **Python:** 3.12+
- **Status:** Actively developed

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

- [Memory-FS](https://github.com/owasp-sbot/Memory-FS) -- Pluggable filesystem abstraction
- [MGraph-DB](https://github.com/owasp-sbot/MGraph-DB) -- Graph database operations
- [OSBot-Utils](https://github.com/owasp-sbot/OSBot-Utils) -- Type_Safe utilities

## Use Cases

- **Git-native issue tracking** -- Store issues alongside code, branch/merge with PRs
- **Offline-first workflows** -- Full functionality without network access
- **Custom integrations** -- Simple JSON format for easy tooling
- **Hierarchical project management** -- Organize epics > features > tasks > subtasks
- **Embedded issue tracking** -- Add issue tracking to any Python application
- **AI agent collaboration** -- Agents read and write issues as structured graph nodes

## License

Apache License 2.0 -- see [LICENSE](LICENSE) for details.
