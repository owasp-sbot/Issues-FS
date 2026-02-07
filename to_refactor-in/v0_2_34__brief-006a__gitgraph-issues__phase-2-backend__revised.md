# Backend Implementation Brief: Phase 2 — Tasks B10-B22

**Document:** brief-006a__gitgraph-issues__phase-2-backend  
**Version:** v2.0 (Revised)  
**Date:** 2026-02-03  
**Author:** Architecture Session  
**Status:** Ready for Implementation  
**Project:** GitGraph Issues

---

## Overview

This brief provides detailed implementation specifications for Phase 2 backend tasks. These changes enable:
- Finding issues in nested `issues/` folders (recursive discovery)
- Removing legacy `node.json` support (cleanup)
- Config file management via API (extend existing `Type__Service`)
- MGraphDB-based efficient data access (four-layer architecture)
- Hyphenated label support (`User-Story-1`)

---

## Implementation Order

```
Priority 0 (Critical Path — Blocks UI):
  B10 → B11 → B14
  
Priority 1 (Cleanup — No UI Dependency):
  B12 → B13 (requires migration script first)
  
Priority 2 (Features — Parallel OK):
  B15, B16, B17, B22
  
Priority 3 (MGraphDB — Can Start After P0):
  B18 → B19 → B20 → B21
```

### Dependency Graph

```
B10 (recursive discovery)
 └─→ B11 (path loading)
      └─→ B14 (path endpoint)
           └─→ B17 (root scoping)

B12 (delete node.json on save) ─→ B13 (remove fallback)

B18 (MGraphDB schema)
 └─→ B19 (sync service)
      ├─→ B20 (query endpoints)
      └─→ B21 (viz endpoints)
```

---

## Coding Patterns Reference

**CRITICAL:** All code must follow these established patterns. Deviations will cause runtime errors or break consistency.

### Type_Safe Rules

```python
# ✅ CORRECT: Inherit Type_Safe, use Safe_* primitives
class Schema__Node__Info(Type_Safe):
    label     : Safe_Str__Node_Label
    path      : Safe_Str__File__Path
    node_type : Safe_Str__Node_Type

# ❌ WRONG: Never use @dataclass
@dataclass
class Node__Info:
    label: str
```

### Method Decorators

```python
# ✅ CORRECT: Use @type_safe on public methods
@type_safe
def node_load_by_path(self                           ,
                      folder_path : Safe_Str__File__Path
                 ) -> Schema__Node:

# ❌ WRONG: Missing decorator
def node_load_by_path(self, folder_path: str) -> Schema__Node:
```

### Boolean Checks

```python
# ✅ CORRECT: Explicit is True / is False
if self.storage_fs.file__exists(path) is False:
    return None

# ❌ WRONG: Implicit boolean
if not self.storage_fs.file__exists(path):
    return None
```

### Helper Methods

```python
# ✅ CORRECT: No underscore prefix
def delete_legacy_node_json(self, node_type, label) -> bool:

# ❌ WRONG: Underscore prefix
def _delete_legacy_node_json(self, node_type, label) -> bool:
```

### Alignment

```python
# ✅ CORRECT: Imports aligned at column 70-80
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                             import Safe_UInt

# ✅ CORRECT: Inline comments aligned at column 70-80
class Graph__Repository(Type_Safe):                                              # Memory-FS based graph repository
    memory_fs    : Memory_FS                                                     # Storage abstraction
    path_handler : Path__Handler__Graph_Node                                     # Path generation
```

### Section Headers

```python
# ═══════════════════════════════════════════════════════════════════════════════
# Node Discovery (Phase 2: Recursive Search)
# ═══════════════════════════════════════════════════════════════════════════════
```

### Schema Rules (MGraphDB Four-Layer Pattern)

```python
# ✅ CORRECT: Schema = pure data, NO methods
class Schema__MGraph__Issue__Node(Type_Safe):
    node_id   : Node_Id
    label     : Safe_Str__Node_Label
    title     : Safe_Str__Text

# ❌ WRONG: Methods in schema
class MGraph__Issue__Node(Type_Safe):
    node_id   : Node_Id
    def get_children(self): ...  # NO! Move to Domain layer
```

---

## B10: Recursive Node Discovery

### Objective

Update `Graph__Repository` to find ALL `issue.json` files recursively, including nested `issues/` subfolders.

### Problem

Current code only searches `data/{type}/{label}/` — misses issues at:
```
data/project/Project-1/issues/Version-1/issue.json
data/project/Project-1/issues/Version-1/issues/Task-6/issue.json
```

### Implementation

**File:** `mgraph_ai_ui_html_transformation_workbench/schemas/graph/Schema__Node__Info.py` (NEW)

```python
# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Info - Node discovery result (Phase 2)
# Pure data container for recursive node discovery
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types import Safe_Str__Node_Type, Safe_Str__Node_Label


class Schema__Node__Info(Type_Safe):                                             # Node discovery info
    label     : Safe_Str__Node_Label                                             # e.g., "Task-6"
    path      : Safe_Str__File__Path                                             # e.g., "data/project/Project-1/issues/..."
    node_type : Safe_Str__Node_Type                                              # e.g., "task"
```

**File:** `Graph__Repository.py`

Add these imports at the top (aligned at column 70-80):
```python
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Info import Schema__Node__Info
```

Add these methods:
```python
    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Discovery (Phase 2: Recursive Search)
    # ═══════════════════════════════════════════════════════════════════════════════

    SKIP_LABELS = {'config', 'data', 'issues', 'indexes', '.issues'}             # System folder names

    @type_safe
    def nodes_list_all(self                               ,                      # Find all issues recursively
                       root_path : Safe_Str__File__Path = None
                  ) -> List[Schema__Node__Info]:
        all_paths = self.storage_fs.files__paths()
        nodes     = []

        for path in all_paths:
            if path.endswith('/issue.json') is False:                            # Only issue.json files
                continue

            if root_path is not None and str(root_path) != '':                   # Filter by root if specified
                if self.is_path_under_root(path, root_path) is False:
                    continue

            folder_path = path.rsplit('/issue.json', 1)[0]                       # Extract folder path
            label       = folder_path.rsplit('/', 1)[-1]                         # Extract label from path

            if label in self.SKIP_LABELS:                                        # Skip system folders
                continue

            node_type = self.extract_node_type_from_file(path)                   # Read type from JSON

            node_info = Schema__Node__Info(label     = Safe_Str__Node_Label(label)      ,
                                           path      = Safe_Str__File__Path(folder_path),
                                           node_type = Safe_Str__Node_Type(node_type)   )
            nodes.append(node_info)

        return nodes

    @type_safe
    def is_path_under_root(self                              ,                   # Check path containment
                           file_path : Safe_Str__File__Path  ,
                           root_path : Safe_Str__File__Path
                      ) -> bool:
        file_str = str(file_path)
        root_str = str(root_path)

        if root_str == '':                                                       # Empty root = match all
            return True

        if root_str.endswith('/'):                                               # Normalize root path
            return file_str.startswith(root_str)

        return file_str.startswith(f"{root_str}/")

    @type_safe
    def extract_node_type_from_file(self                              ,          # Get node_type from JSON
                                    file_path : Safe_Str__File__Path
                               ) -> str:
        try:
            content = self.storage_fs.file__str(str(file_path))
            if content:
                data = json_loads(content)
                return data.get('node_type', '')
        except (ValueError, KeyError):                                           # JSON parse or key errors
            pass
        return ''
```

**Update existing `nodes_list_labels()` method:**

Replace the existing implementation with:
```python
    @type_safe
    def nodes_list_labels(self                                    ,              # List all node labels for type
                          node_type : Safe_Str__Node_Type = None
                     ) -> List[Safe_Str__Node_Label]:
        all_nodes = self.nodes_list_all()                                        # Phase 2: Use recursive discovery

        if node_type is not None:
            type_str = str(node_type)
            return [n.label for n in all_nodes if str(n.node_type) == type_str]

        return [n.label for n in all_nodes]
```

### Tests

```python
class Test__Graph__Repository__Recursive_Discovery(TestCase):

    def setUp(self):
        self.storage_fs = Storage_FS__Memory()
        self.memory_fs  = Memory_FS(storage_fs=self.storage_fs)
        self.path_handler = Path__Handler__Graph_Node(base_path='')
        self.repository = Graph__Repository(memory_fs=self.memory_fs, path_handler=self.path_handler)

    def create_issue(self, path: str, label: str, node_type: str, title: str = 'Test'):
        data = {'label': label, 'node_type': node_type, 'title': title}
        self.storage_fs.file__save(path, json_dumps(data).encode('utf-8'))

    def test__nodes_list_all__finds_top_level(self):
        self.create_issue('data/task/Task-1/issue.json', label='Task-1', node_type='task')

        nodes  = self.repository.nodes_list_all()
        labels = [str(n.label) for n in nodes]

        assert 'Task-1' in labels, f'Expected Task-1 in {labels}'

    def test__nodes_list_all__finds_nested(self):
        self.create_issue('data/project/Project-1/issue.json', label='Project-1', node_type='project')
        self.create_issue('data/project/Project-1/issues/Version-1/issue.json', label='Version-1', node_type='version')

        nodes  = self.repository.nodes_list_all()
        labels = [str(n.label) for n in nodes]

        assert 'Project-1' in labels, f'Expected Project-1 in {labels}'
        assert 'Version-1' in labels, f'Expected Version-1 in {labels}'

    def test__nodes_list_all__finds_deeply_nested(self):
        self.create_issue('data/project/Project-1/issues/Version-1/issues/Task-1/issue.json',
                          label='Task-1', node_type='task')

        nodes  = self.repository.nodes_list_all()
        labels = [str(n.label) for n in nodes]

        assert 'Task-1' in labels, f'Expected Task-1 in {labels}'

    def test__nodes_list_all__with_root_filter(self):
        self.create_issue('data/project/Project-1/issues/Task-1/issue.json', label='Task-1', node_type='task')
        self.create_issue('data/project/Project-2/issues/Task-2/issue.json', label='Task-2', node_type='task')

        nodes  = self.repository.nodes_list_all(root_path=Safe_Str__File__Path('data/project/Project-1'))
        labels = [str(n.label) for n in nodes]

        assert 'Task-1' in labels    , f'Expected Task-1 in {labels}'
        assert 'Task-2' not in labels, f'Task-2 should not be in {labels}'

    def test__nodes_list_all__skips_system_folders(self):
        self.create_issue('data/issues/issue.json', label='issues', node_type='folder')
        self.create_issue('data/task/Task-1/issue.json', label='Task-1', node_type='task')

        nodes  = self.repository.nodes_list_all()
        labels = [str(n.label) for n in nodes]

        assert 'issues' not in labels, f'System folder "issues" should be skipped'
        assert 'Task-1' in labels    , f'Expected Task-1 in {labels}'
```

---

## B11: Node Loading by Path

### Objective

Add method to load a node by its full folder path (not just label). This enables loading nodes from nested `issues/` folders.

### Implementation

**File:** `Graph__Repository.py`

Add these methods:
```python
    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Loading (Phase 2: Path-Based)
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def node_load_by_path(self                              ,                    # Load by explicit path
                          folder_path : Safe_Str__File__Path
                     ) -> Schema__Node:
        issue_file = f"{folder_path}/issue.json"

        if self.storage_fs.file__exists(issue_file) is False:
            return None

        content = self.storage_fs.file__str(issue_file)
        if not content:
            return None

        data = json_loads(content)
        if data is None:
            return None

        return Schema__Node.from_json(data)

    @type_safe
    def node_find_path_by_label(self                              ,              # Find path for label
                                label : Safe_Str__Node_Label
                           ) -> Safe_Str__File__Path:
        label_str = str(label)
        all_paths = self.storage_fs.files__paths()

        for path in all_paths:
            if path.endswith(f'/{label_str}/issue.json'):
                folder_path = path.rsplit('/issue.json', 1)[0]
                return Safe_Str__File__Path(folder_path)

        return None
```

**Update existing `node_load()` signature and implementation:**

The current signature is:
```python
def node_load(self, node_type: Safe_Str__Node_Type, label: Safe_Str__Node_Label) -> Schema__Node:
```

We need to add an **overloaded version** that searches by label only. Add this new method (keep the original for backward compatibility):
```python
    @type_safe
    def node_load_by_label(self                              ,                   # Load by label (recursive search)
                           label : Safe_Str__Node_Label
                      ) -> Schema__Node:
        path = self.node_find_path_by_label(label)

        if path is not None:
            return self.node_load_by_path(path)

        return None
```

**File:** `Node__Service.py`

Add this method:
```python
    @type_safe
    def get_node_by_path(self                              ,                     # Get by explicit folder path
                         folder_path : Safe_Str__File__Path
                    ) -> Schema__Node__Response:
        node = self.repository.node_load_by_path(folder_path)

        if node is not None:
            return Schema__Node__Response(success = True ,
                                          node    = node )

        return Schema__Node__Response(success = False                              ,
                                      message = f'Node not found at: {folder_path}')
```

### Tests

```python
def test__node_load_by_path__nested(self):
    self.create_issue('data/project/Project-1/issues/Version-1/issue.json',
                      label='Version-1', node_type='version', title='v0.1.0')

    node = self.repository.node_load_by_path(Safe_Str__File__Path('data/project/Project-1/issues/Version-1'))

    assert node is not None
    assert str(node.label) == 'Version-1'
    assert str(node.title) == 'v0.1.0'

def test__node_load_by_label__finds_nested(self):
    self.create_issue('data/project/Project-1/issues/Version-1/issue.json',
                      label='Version-1', node_type='version')

    node = self.repository.node_load_by_label(Safe_Str__Node_Label('Version-1'))

    assert node is not None
    assert str(node.label) == 'Version-1'

def test__node_find_path_by_label__returns_correct_path(self):
    self.create_issue('data/project/Project-1/issues/Task-6/issue.json',
                      label='Task-6', node_type='task')

    path = self.repository.node_find_path_by_label(Safe_Str__Node_Label('Task-6'))

    assert path is not None
    assert str(path) == 'data/project/Project-1/issues/Task-6'
```

---

## B12: Remove node.json Write (Delete on Save)

### Objective

When saving a node, delete any existing `node.json` file (progressive cleanup).

### Implementation

**File:** `Graph__Repository.py`

**Important:** Keep the existing `node_save()` signature unchanged. The node already contains `node_type` and `label`.

Update the existing `node_save()` method:
```python
    @type_safe
    def node_save(self, node: Schema__Node) -> bool:                             # Save node to issue.json
        if not node.label:
            return False

        path_issue = self.path_handler.path_for_issue_json(node_type = node.node_type,
                                                           label     = node.label    )
        data       = node.json()
        content    = json_dumps(data, indent=2)
        result     = self.storage_fs.file__save(path_issue, content.encode('utf-8'))

        if result is True:                                                       # Phase 2: Delete legacy file
            self.delete_legacy_node_json(node.node_type, node.label)

        return result

    @type_safe
    def delete_legacy_node_json(self                              ,              # Remove legacy node.json
                                node_type : Safe_Str__Node_Type   ,
                                label     : Safe_Str__Node_Label
                           ) -> bool:
        path_node = self.path_handler.path_for_node_json(node_type, label)

        if self.storage_fs.file__exists(path_node) is True:
            return self.storage_fs.file__delete(path_node)

        return False
```

### Tests

```python
def test__node_save__deletes_legacy_node_json(self):
    # Create both files manually
    self.storage_fs.file__save('data/task/Task-1/node.json', b'{"label":"Task-1","node_type":"task"}')
    self.storage_fs.file__save('data/task/Task-1/issue.json', b'{"label":"Task-1","node_type":"task"}')

    # Load and save the node
    node = self.repository.node_load(node_type=Safe_Str__Node_Type('task'),
                                     label=Safe_Str__Node_Label('Task-1'))
    self.repository.node_save(node)

    # Verify node.json was deleted
    assert self.storage_fs.file__exists('data/task/Task-1/issue.json') is True
    assert self.storage_fs.file__exists('data/task/Task-1/node.json') is False

def test__node_save__handles_missing_node_json(self):
    # Create only issue.json
    self.storage_fs.file__save('data/task/Task-2/issue.json', b'{"label":"Task-2","node_type":"task"}')

    node = self.repository.node_load(node_type=Safe_Str__Node_Type('task'),
                                     label=Safe_Str__Node_Label('Task-2'))
    result = self.repository.node_save(node)

    assert result is True
    assert self.storage_fs.file__exists('data/task/Task-2/issue.json') is True
```

---

## B13: Remove node.json Read Fallback

### Objective

Remove the fallback that reads `node.json` when `issue.json` doesn't exist.

### Prerequisites

**CRITICAL:** Run migration script BEFORE deploying B13 changes. The migration converts all remaining `node.json` files to `issue.json`.

### Migration Script

**File:** `scripts/migrate_node_to_issue_json.py` (NEW)

```python
# ═══════════════════════════════════════════════════════════════════════════════
# Migration Script: Convert all node.json → issue.json
# Run this BEFORE deploying B13 changes
#
# Usage:
#   python -m scripts.migrate_node_to_issue_json --path /path/to/.issues
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                   import type_safe
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository import Graph__Repository


class Migration__Node_To_Issue_Json(Type_Safe):                                  # Migration runner
    repository : Graph__Repository

    @type_safe
    def run(self) -> dict:                                                       # Execute migration
        all_paths = self.repository.storage_fs.files__paths()
        results   = {'converted': 0, 'deleted': 0, 'skipped': 0, 'errors': []}

        for path in all_paths:
            if path.endswith('/node.json') is False:
                continue

            issue_path = path.replace('/node.json', '/issue.json')

            try:
                if self.repository.storage_fs.file__exists(issue_path) is True:
                    # issue.json already exists, just delete node.json
                    self.repository.storage_fs.file__delete(path)
                    results['deleted'] += 1
                else:
                    # Copy node.json → issue.json, then delete node.json
                    content = self.repository.storage_fs.file__bytes(path)
                    self.repository.storage_fs.file__save(issue_path, content)
                    self.repository.storage_fs.file__delete(path)
                    results['converted'] += 1
            except Exception as e:
                results['errors'].append(f'{path}: {str(e)}')

        return results


def main():
    import argparse
    from memory_fs.Memory_FS import Memory_FS
    from memory_fs.storage_fs.providers.Storage_FS__Local_Disk import Storage_FS__Local_Disk
    from mgraph_ai_ui_html_transformation_workbench.service.issues.storage.Path__Handler__Graph_Node import Path__Handler__Graph_Node

    parser = argparse.ArgumentParser(description='Migrate node.json to issue.json')
    parser.add_argument('--path', required=True, help='Path to .issues folder')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    args = parser.parse_args()

    storage_fs   = Storage_FS__Local_Disk(root_path=args.path)
    memory_fs    = Memory_FS(storage_fs=storage_fs)
    path_handler = Path__Handler__Graph_Node(base_path='')
    repository   = Graph__Repository(memory_fs=memory_fs, path_handler=path_handler)

    if args.dry_run:
        all_paths  = storage_fs.files__paths()
        node_files = [p for p in all_paths if p.endswith('/node.json')]
        print(f'Found {len(node_files)} node.json files to migrate:')
        for path in node_files:
            print(f'  {path}')
        return

    migration = Migration__Node_To_Issue_Json(repository=repository)
    results   = migration.run()

    print(f'Migration complete:')
    print(f'  Converted: {results["converted"]}')
    print(f'  Deleted:   {results["deleted"]} (had both files)')
    print(f'  Errors:    {len(results["errors"])}')

    if results['errors']:
        print('Errors:')
        for error in results['errors']:
            print(f'  {error}')


if __name__ == '__main__':
    main()
```

### Implementation

**File:** `Graph__Repository.py`

Replace `get_issue_file_path()`:
```python
    @type_safe
    def get_issue_file_path(self                              ,                  # Get issue file path (issue.json only)
                            node_type : Safe_Str__Node_Type   ,
                            label     : Safe_Str__Node_Label
                       ) -> str:
        return self.path_handler.path_for_issue_json(node_type, label)           # Phase 2: No node.json fallback
```

**File:** `Root__Selection__Service.py`

Update `is_valid_root()` — remove node.json check:
```python
    def is_valid_root(self, path: str) -> bool:                                  # Check if path is a valid root
        if not path:
            return True                                                          # Empty path = default root

        base_path = str(self.path_handler.base_path)

        if base_path and base_path != '.':
            if path == base_path:
                return True

        full_path = path
        if base_path and base_path != '.':
            if path.startswith(base_path) is False:
                full_path = f"{base_path}/{path}"

        issue_json = f"{full_path}/{FILE_NAME__ISSUE_JSON}"

        return self.repository.storage_fs.file__exists(issue_json)               # Phase 2: issue.json only
```

Update `scan_for_issue_folders()`:
```python
    def scan_for_issue_folders(self) -> List[str]:                               # Find all folders with issue.json
        folders     = set()
        all_paths   = self.repository.storage_fs.files__paths()
        base_path   = str(self.path_handler.base_path)
        data_prefix = f"{base_path}/data/" if base_path and base_path != '.' else "data/"

        for path in all_paths:
            if path.startswith(data_prefix) is False:
                continue

            if path.endswith(f'/{FILE_NAME__ISSUE_JSON}'):                       # Phase 2: issue.json only
                folder = path.rsplit('/', 1)[0]
                if folder != base_path and folder != '.':
                    folders.add(folder)

        return list(folders)
```

**File:** `Issue__Children__Service.py`

Update `scan_child_folders()`:
```python
    @type_safe
    def scan_child_folders(self                              ,                   # Find all child folders in issues/
                           issues_folder : Safe_Str__File__Path
                      ) -> List[Safe_Str__File__Path]:
        folders   = set()
        all_paths = self.repository.storage_fs.files__paths()
        prefix    = f"{issues_folder}/"

        for path in all_paths:
            if path.startswith(prefix) is False:
                continue

            relative = path[len(prefix):]
            parts    = relative.split('/')

            if len(parts) >= 2:
                child_folder = parts[0]
                filename     = parts[1]

                if filename == FILE_NAME__ISSUE_JSON:                            # Phase 2: issue.json only
                    folders.add(f"{issues_folder}/{child_folder}")

        return list(folders)
```

Update `load_child_summary()`:
```python
    def load_child_summary(self                              ,                   # Load summary data for child
                           child_folder : Safe_Str__File__Path
                      ) -> dict:
        issue_path = f"{child_folder}/{FILE_NAME__ISSUE_JSON}"
        data       = self.load_issue_from_path(issue_path)

        if data:
            data['path'] = self.make_relative_path(child_folder)
            return data

        return None                                                              # Phase 2: No node.json fallback
```

---

## B14: Path-Based Node Endpoint

### Objective

Add endpoint to load node by hierarchical path (e.g., `Project-1/Version-1/Task-6`).

### Endpoint

```
GET /nodes/api/node/by-path?path={hierarchical_path}
```

### Dependency Injection Setup

**CRITICAL:** `Node__Service` needs access to `Root__Selection__Service` to resolve paths relative to the current root. This requires updating the wire-up.

**File:** `Node__Service.py`

Add the new dependency:
```python
from mgraph_ai_ui_html_transformation_workbench.service.issues.phase_1.Root__Selection__Service import Root__Selection__Service

class Node__Service(Type_Safe):                                                  # Node business logic service
    repository             : Graph__Repository                                   # Data access layer
    root_selection_service : Root__Selection__Service = None                     # Phase 2: Root context (optional)
```

Add the path resolution methods:
```python
    # ═══════════════════════════════════════════════════════════════════════════════
    # Path Resolution (Phase 2)
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def resolve_hierarchical_path(self                     ,                     # Convert hierarchical to filesystem path
                                  path         : str       ,
                                  current_root : str = ''
                             ) -> str:
        """
        Convert 'Project-1/Version-1/Task-6' to filesystem path.

        If current_root is set (e.g., 'data/project/Project-1'), then:
          'Version-1/Task-6' → 'data/project/Project-1/issues/Version-1/issues/Task-6'

        If no root, searches for first segment globally:
          'Project-1/Version-1' → 'data/project/Project-1/issues/Version-1'
        """
        if not path:
            return current_root if current_root else None

        segments = path.split('/')

        if current_root:
            result    = current_root                                             # Start from root
            start_idx = 0
        else:
            first_label = segments[0]                                            # Find first segment
            result      = self.repository.node_find_path_by_label(
                              Safe_Str__Node_Label(first_label))

            if result is None:
                return None

            result    = str(result)
            start_idx = 1

        for segment in segments[start_idx:]:                                     # Each segment in issues/ subfolder
            result = f"{result}/issues/{segment}"

        return result

    @type_safe
    def get_node_by_hierarchical_path(self                     ,                 # Get by hierarchical path
                                      path : str
                                 ) -> Schema__Node__Response:
        current_root = ''

        if self.root_selection_service is not None:
            current_root = str(self.root_selection_service.current_root)

        resolved = self.resolve_hierarchical_path(path, current_root)

        if resolved is None:
            return Schema__Node__Response(success = False                         ,
                                          message = f'Cannot resolve path: {path}')

        node = self.repository.node_load_by_path(Safe_Str__File__Path(resolved))

        if node is not None:
            return Schema__Node__Response(success = True ,
                                          node    = node )

        return Schema__Node__Response(success = False                            ,
                                      message = f'Node not found at: {resolved}')
```

**File:** `Routes__Nodes.py`

Add the endpoint:
```python
    @route_path('/nodes/api/node/by-path')
    def get_node_by_path(self, path: str) -> Schema__Node__Response:             # GET by hierarchical path
        return self.service.get_node_by_hierarchical_path(path)
```

**File:** `Html_Transformation_Workbench__Fast_API.py`

Update the wire-up in `setup_services()`:
```python
        # Core services - Phase 2: Node service needs root selection
        self.type_service     = Type__Service    (repository = self.graph_repository)
        self.node_service     = Node__Service    (repository             = self.graph_repository      ,
                                                  root_selection_service = self.root_selection_service)
        self.link_service     = Link__Service    (repository = self.graph_repository)
        self.comments_service = Comments__Service(repository = self.graph_repository)
```

### Tests

```python
def test__get_node_by_hierarchical_path__single_segment(self):
    self.create_issue('data/project/Project-1/issue.json', label='Project-1', node_type='project')

    response = self.service.get_node_by_hierarchical_path('Project-1')

    assert response.success is True
    assert str(response.node.label) == 'Project-1'

def test__get_node_by_hierarchical_path__multiple_segments(self):
    self.create_issue('data/project/Project-1/issue.json', label='Project-1', node_type='project')
    self.create_issue('data/project/Project-1/issues/Version-1/issue.json', label='Version-1', node_type='version')
    self.create_issue('data/project/Project-1/issues/Version-1/issues/Task-6/issue.json', label='Task-6', node_type='task')

    response = self.service.get_node_by_hierarchical_path('Project-1/Version-1/Task-6')

    assert response.success is True
    assert str(response.node.label) == 'Task-6'

def test__get_node_by_hierarchical_path__with_root(self):
    self.create_issue('data/project/Project-1/issues/Version-1/issue.json', label='Version-1', node_type='version')

    self.service.root_selection_service.current_root = Safe_Str__File__Path('data/project/Project-1')

    response = self.service.get_node_by_hierarchical_path('Version-1')

    assert response.success is True
    assert str(response.node.label) == 'Version-1'

def test__get_node_by_hierarchical_path__not_found(self):
    response = self.service.get_node_by_hierarchical_path('NonExistent/Path')

    assert response.success is False
    assert 'Cannot resolve' in str(response.message)
```

---

## B15: Config CRUD API - Node Types (Extend Type__Service)

### Objective

Add REST endpoints to manage `node-types.json`. **Note:** We extend the existing `Type__Service` rather than creating a new `Config__Service` to avoid duplication.

### Existing Functionality in Type__Service

The `Type__Service` already has:
- `list_node_types()` ✓
- `get_node_type(name)` ✓
- `create_node_type(...)` ✓
- `delete_node_type(name)` ✓

### New: Add Update Method

**File:** `Type__Service.py`

Add the update method:
```python
    @type_safe
    def update_node_type(self                                  ,                 # Update existing node type
                         name       : Safe_Str__Node_Type      ,
                         updates    : Schema__Node__Type__Update
                    ) -> Schema__Node__Type__Response:
        node_types = self.repository.node_types_load()

        found_idx = None
        for idx, nt in enumerate(node_types):
            if str(nt.name) == str(name):
                found_idx = idx
                break

        if found_idx is None:
            return Schema__Node__Type__Response(success = False                    ,
                                                message = f'Node type not found: {name}')

        existing = node_types[found_idx]

        # Apply updates (only non-None fields)
        if updates.display_name is not None:
            existing.display_name = updates.display_name
        if updates.color is not None:
            existing.color = updates.color
        if updates.icon is not None:
            existing.icon = updates.icon
        if updates.statuses is not None:
            existing.statuses = updates.statuses
        if updates.default_status is not None:
            existing.default_status = updates.default_status

        node_types[found_idx] = existing
        self.repository.node_types_save(node_types)

        return Schema__Node__Type__Response(success   = True    ,
                                            node_type = existing)
```

**File:** `schemas/graph/Schema__Node__Type.py`

Add the update schema:
```python
class Schema__Node__Type__Update(Type_Safe):                                     # Update request for node type
    display_name   : Safe_Str__Text   = None                                     # Optional: new display name
    color          : Safe_Str__Text   = None                                     # Optional: new color
    icon           : Safe_Str__Text   = None                                     # Optional: new icon
    statuses       : List[str]        = None                                     # Optional: new statuses
    default_status : Safe_Str__Status = None                                     # Optional: new default
```

### New Endpoints

**File:** `Routes__Types.py`

Add the PUT endpoint:
```python
    @route_path('/types/api/node-types/{name}')
    def update_node_type(self                                  ,                 # PUT: Update node type
                         name    : str                         ,
                         updates : Schema__Node__Type__Update
                    ) -> Schema__Node__Type__Response:
        return self.service.update_node_type(name    = Safe_Str__Node_Type(name),
                                             updates = updates                  )
```

### Full REST Endpoint Summary

```
GET    /types/api/node-types           # List all (existing)
GET    /types/api/node-types/{name}    # Get one (existing)
POST   /types/api/node-types           # Create (existing)
PUT    /types/api/node-types/{name}    # Update (NEW)
DELETE /types/api/node-types/{name}    # Delete (existing)
```

---

## B16: Config CRUD API - Link Types (Extend Type__Service)

### Objective

Add REST endpoints to manage `link-types.json`, following the same pattern as B15.

### Implementation

Same pattern as B15. Add to `Type__Service`:
- `update_link_type(name, updates)` method

Add to `Routes__Types`:
- `PUT /types/api/link-types/{name}` endpoint

### Full REST Endpoint Summary

```
GET    /types/api/link-types           # List all (existing)
GET    /types/api/link-types/{name}    # Get one (existing)
POST   /types/api/link-types           # Create (existing)
PUT    /types/api/link-types/{name}    # Update (NEW)
DELETE /types/api/link-types/{name}    # Delete (existing)
```

---

## B17: Root Scoping Verification

### Objective

Ensure setting root correctly filters all query results.

### Implementation

**File:** `Node__Service.py`

Update `list_nodes()` to filter by root:
```python
    def list_nodes(self                                       ,                  # List nodes, optionally filtered
                   node_type : Safe_Str__Node_Type = None
              ) -> Schema__Node__List__Response:
        current_root = None

        if self.root_selection_service is not None:                              # Phase 2: Apply root filter
            root_str = str(self.root_selection_service.current_root)
            if root_str:
                current_root = Safe_Str__File__Path(root_str)

        summaries = []

        if node_type:
            summaries = self.list_nodes_for_type(node_type, current_root)
        else:
            node_types = self.repository.node_types_load()
            for nt in node_types:
                type_summaries = self.list_nodes_for_type(nt.name, current_root)
                summaries.extend(type_summaries)

        return Schema__Node__List__Response(success = True           ,
                                            nodes   = summaries      ,
                                            total   = len(summaries) )

    def list_nodes_for_type(self                                       ,         # List nodes for specific type
                            node_type    : Safe_Str__Node_Type         ,
                            root_path    : Safe_Str__File__Path = None
                       ) -> List[Schema__Node__Summary]:
        summaries = []
        all_nodes = self.repository.nodes_list_all(root_path=root_path)          # Phase 2: Use recursive with filter

        for node_info in all_nodes:
            if str(node_info.node_type) != str(node_type):
                continue

            node = self.repository.node_load_by_path(node_info.path)
            if node:
                summary = Schema__Node__Summary(label     = node.label     ,
                                                node_type = node.node_type ,
                                                title     = node.title     ,
                                                status    = node.status    )
                summaries.append(summary)

        return summaries
```

### Tests

```python
def test__list_nodes__respects_root(self):
    # Create issues in two projects
    self.create_issue('data/project/Project-1/issues/Task-1/issue.json',
                      label='Task-1', node_type='task')
    self.create_issue('data/project/Project-2/issues/Task-2/issue.json',
                      label='Task-2', node_type='task')

    # Set root to Project-1
    self.service.root_selection_service.current_root = Safe_Str__File__Path('data/project/Project-1')

    # List all nodes
    response = self.service.list_nodes()
    labels   = [str(n.label) for n in response.nodes]

    assert 'Task-1' in labels    , f'Expected Task-1 in {labels}'
    assert 'Task-2' not in labels, f'Task-2 should not be in {labels}'

def test__list_nodes__no_root_returns_all(self):
    self.create_issue('data/project/Project-1/issues/Task-1/issue.json',
                      label='Task-1', node_type='task')
    self.create_issue('data/project/Project-2/issues/Task-2/issue.json',
                      label='Task-2', node_type='task')

    # No root set
    self.service.root_selection_service.current_root = Safe_Str__File__Path('')

    response = self.service.list_nodes()
    labels   = [str(n.label) for n in response.nodes]

    assert 'Task-1' in labels, f'Expected Task-1 in {labels}'
    assert 'Task-2' in labels, f'Expected Task-2 in {labels}'
```

---

## B18: MGraphDB Schema Design

### Objective

Define MGraph schema for issue data following the **four-layer architecture**:
1. **Schema Layer** — Pure data containers (NO methods)
2. **Model Layer** — Basic CRUD operations
3. **Domain Layer** — Business logic and indexes
4. **Action Layer** — Complex algorithms

### Storage

`.issues/indexes/issues.mgraph.json`

### Implementation

**File:** `mgraph/Schema__MGraph__Issues.py` (NEW)

```python
# ═══════════════════════════════════════════════════════════════════════════════
# Schema__MGraph__Issues - Pure data schemas for MGraphDB issue storage
# CRITICAL: Schema classes contain ONLY type annotations - NO methods
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import Dict, List
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                import Edge_Id
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text     import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status


class Schema__MGraph__Issue__Node(Type_Safe):                                    # Issue node data
    node_id   : Node_Id                                                          # Unique identifier
    label     : Safe_Str__Node_Label                                             # Display label (e.g., "Task-6")
    title     : Safe_Str__Text                                                   # Human-readable title
    node_type : Safe_Str__Node_Type                                              # Type (e.g., "task")
    status    : Safe_Str__Status                                                 # Current status
    file_path : Safe_Str__File__Path                                             # Filesystem path to issue.json


class Schema__MGraph__Issue__Edge(Type_Safe):                                    # Issue edge data
    edge_id   : Edge_Id                                                          # Unique identifier
    source_id : Node_Id                                                          # Source node ID
    target_id : Node_Id                                                          # Target node ID
    edge_type : Safe_Str__Text                                                   # 'contains', 'relates-to', etc.


class Schema__MGraph__Issues__Data(Type_Safe):                                   # Graph data container
    nodes : Dict[str, Schema__MGraph__Issue__Node]                               # node_id → node
    edges : Dict[str, Schema__MGraph__Issue__Edge]                               # edge_id → edge
```

**File:** `mgraph/MGraph__Issues__Domain.py` (NEW)

```python
# ═══════════════════════════════════════════════════════════════════════════════
# MGraph__Issues__Domain - Business logic for issue graph operations
# Contains indexes and query methods - NO data storage
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import Dict, List
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                   import type_safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                import Edge_Id
from mgraph_ai_ui_html_transformation_workbench.mgraph.Schema__MGraph__Issues    import (
    Schema__MGraph__Issue__Node, Schema__MGraph__Issue__Edge, Schema__MGraph__Issues__Data
)
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types import Safe_Str__Node_Label


class MGraph__Issues__Domain(Type_Safe):                                         # Graph domain operations
    data : Schema__MGraph__Issues__Data                                          # Underlying data

    # Indexes (computed, not persisted)
    index_by_label  : Dict[str, str]                                             # label → node_id
    index_by_path   : Dict[str, str]                                             # path → node_id
    index_by_parent : Dict[str, List[str]]                                       # parent_id → [child_ids]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.data is None:
            self.data = Schema__MGraph__Issues__Data(nodes={}, edges={})
        if self.index_by_label is None:
            self.index_by_label = {}
        if self.index_by_path is None:
            self.index_by_path = {}
        if self.index_by_parent is None:
            self.index_by_parent = {}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def add_node(self, node: Schema__MGraph__Issue__Node) -> str:                # Add node and update indexes
        node_id_str = str(node.node_id)

        self.data.nodes[node_id_str] = node

        # Update indexes
        self.index_by_label[str(node.label)]     = node_id_str
        self.index_by_path[str(node.file_path)]  = node_id_str

        return node_id_str

    @type_safe
    def get_node_by_label(self                              ,                    # Query by label
                          label : Safe_Str__Node_Label
                     ) -> Schema__MGraph__Issue__Node:
        node_id = self.index_by_label.get(str(label))

        if node_id is None:
            return None

        return self.data.nodes.get(node_id)

    @type_safe
    def get_node_by_path(self, path: str) -> Schema__MGraph__Issue__Node:        # Query by file path
        node_id = self.index_by_path.get(path)

        if node_id is None:
            return None

        return self.data.nodes.get(node_id)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def add_edge(self, edge: Schema__MGraph__Issue__Edge) -> str:                # Add edge and update indexes
        edge_id_str   = str(edge.edge_id)
        source_id_str = str(edge.source_id)
        target_id_str = str(edge.target_id)

        self.data.edges[edge_id_str] = edge

        # Update parent-child index for 'contains' edges
        if str(edge.edge_type) == 'contains':
            if source_id_str not in self.index_by_parent:
                self.index_by_parent[source_id_str] = []
            self.index_by_parent[source_id_str].append(target_id_str)

        return edge_id_str

    @type_safe
    def get_children(self, parent_id: Node_Id) -> List[Schema__MGraph__Issue__Node]:
        parent_id_str = str(parent_id)
        child_ids     = self.index_by_parent.get(parent_id_str, [])

        children = []
        for child_id in child_ids:
            child_node = self.data.nodes.get(child_id)
            if child_node is not None:
                children.append(child_node)

        return children

    @type_safe
    def get_ancestors(self                     ,                                 # Get path to root
                      node_id : Node_Id
                 ) -> List[Schema__MGraph__Issue__Node]:
        ancestors     = []
        current_id    = str(node_id)
        visited       = set()

        while current_id and current_id not in visited:
            visited.add(current_id)

            # Find parent edge
            parent_id = None
            for edge in self.data.edges.values():
                if str(edge.edge_type) == 'contains' and str(edge.target_id) == current_id:
                    parent_id = str(edge.source_id)
                    break

            if parent_id is None:
                break

            parent_node = self.data.nodes.get(parent_id)
            if parent_node is not None:
                ancestors.append(parent_node)

            current_id = parent_id

        return ancestors

    # ═══════════════════════════════════════════════════════════════════════════════
    # Utility Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def clear(self) -> None:                                                     # Reset all data and indexes
        self.data.nodes.clear()
        self.data.edges.clear()
        self.index_by_label.clear()
        self.index_by_path.clear()
        self.index_by_parent.clear()

    def all_nodes(self) -> List[Schema__MGraph__Issue__Node]:                    # Get all nodes
        return list(self.data.nodes.values())
```

---

## B19: MGraphDB Sync Service

### Objective

Sync filesystem to MGraphDB with lazy loading and root change support.

### Implementation

**File:** `services/MGraph__Issues__Sync__Service.py` (NEW)

```python
# ═══════════════════════════════════════════════════════════════════════════════
# MGraph__Issues__Sync__Service - Syncs filesystem to MGraphDB
# Handles lazy loading, root changes, and persistence
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import Dict
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                   import type_safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                import Edge_Id
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.utils.Json                                                      import json_dumps, json_loads
from mgraph_ai_ui_html_transformation_workbench.mgraph.Schema__MGraph__Issues    import Schema__MGraph__Issue__Node, Schema__MGraph__Issue__Edge
from mgraph_ai_ui_html_transformation_workbench.mgraph.MGraph__Issues__Domain    import MGraph__Issues__Domain
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository import Graph__Repository
from mgraph_ai_ui_html_transformation_workbench.service.issues.storage.Path__Handler__Graph_Node import Path__Handler__Graph_Node


class MGraph__Issues__Sync__Service(Type_Safe):                                  # Sync service
    graph        : MGraph__Issues__Domain        = None                          # Graph domain object
    repository   : Graph__Repository                                             # Data access
    path_handler : Path__Handler__Graph_Node                                     # Path generation
    is_loaded    : bool                          = False                         # Lazy load flag
    current_root : Safe_Str__File__Path          = None                          # Current root filter

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.graph is None:
            self.graph = MGraph__Issues__Domain()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Lazy Loading
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def ensure_loaded(self                                       ,               # Lazy load graph
                      root : Safe_Str__File__Path = None
                 ) -> MGraph__Issues__Domain:
        root_str    = str(root) if root else ''
        current_str = str(self.current_root) if self.current_root else ''

        if self.is_loaded is False or root_str != current_str:
            self.full_sync(root)

        return self.graph

    @type_safe
    def on_root_change(self, new_root: Safe_Str__File__Path) -> None:            # Root change trigger
        new_root_str = str(new_root) if new_root else ''
        current_str  = str(self.current_root) if self.current_root else ''

        if new_root_str != current_str:
            self.full_sync(new_root)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Full Sync
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def full_sync(self                                       ,                   # Rebuild graph from filesystem
                  root : Safe_Str__File__Path = None
             ) -> Dict:
        self.graph.clear()
        self.current_root = root

        nodes = self.repository.nodes_list_all(root_path=root)
        stats = {'nodes_added': 0, 'edges_added': 0}

        # Add all nodes
        for info in nodes:
            node_data = self.repository.node_load_by_path(info.path)

            if node_data is None:
                continue

            graph_node = Schema__MGraph__Issue__Node(
                node_id   = node_data.node_id if hasattr(node_data, 'node_id') else Node_Id(),
                label     = node_data.label     ,
                title     = node_data.title     ,
                node_type = node_data.node_type ,
                status    = node_data.status    ,
                file_path = info.path           )

            self.graph.add_node(graph_node)
            stats['nodes_added'] += 1

        # Build containment edges from path structure
        edges_added = self.build_containment_edges()
        stats['edges_added'] = edges_added

        # Persist to disk
        self.save_to_disk()
        self.is_loaded = True

        return stats

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Building
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def build_containment_edges(self) -> int:                                    # Infer parent-child from paths
        edges_added = 0

        for node_id, node in self.graph.data.nodes.items():
            parent_path = self.infer_parent_path(str(node.file_path))

            if parent_path is None:
                continue

            parent_node = self.graph.get_node_by_path(parent_path)

            if parent_node is None:
                continue

            edge = Schema__MGraph__Issue__Edge(
                edge_id   = Edge_Id()           ,
                source_id = parent_node.node_id ,
                target_id = node.node_id        ,
                edge_type = 'contains'          )

            self.graph.add_edge(edge)
            edges_added += 1

        return edges_added

    @type_safe
    def infer_parent_path(self, child_path: str) -> str:                         # Extract parent path
        """
        From 'data/project/Project-1/issues/Version-1'
        returns 'data/project/Project-1'

        From 'data/project/Project-1/issues/Version-1/issues/Task-6'
        returns 'data/project/Project-1/issues/Version-1'
        """
        if '/issues/' not in child_path:
            return None

        parts = child_path.rsplit('/issues/', 1)

        if len(parts) == 2:
            return parts[0]

        return None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Persistence
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def save_to_disk(self) -> bool:                                              # Persist to indexes/
        base_path = str(self.path_handler.base_path) if self.path_handler.base_path else ''

        if base_path and base_path != '.':
            path = f"{base_path}/indexes/issues.mgraph.json"
        else:
            path = "indexes/issues.mgraph.json"

        # Serialize graph data
        data = {
            'nodes': {k: v.json() for k, v in self.graph.data.nodes.items()},
            'edges': {k: v.json() for k, v in self.graph.data.edges.items()},
        }

        content = json_dumps(data, indent=2)
        return self.repository.storage_fs.file__save(path, content.encode('utf-8'))

    @type_safe
    def load_from_disk(self) -> bool:                                            # Load from indexes/
        base_path = str(self.path_handler.base_path) if self.path_handler.base_path else ''

        if base_path and base_path != '.':
            path = f"{base_path}/indexes/issues.mgraph.json"
        else:
            path = "indexes/issues.mgraph.json"

        if self.repository.storage_fs.file__exists(path) is False:
            return False

        content = self.repository.storage_fs.file__str(path)
        if not content:
            return False

        data = json_loads(content)
        if data is None:
            return False

        # Deserialize nodes
        for node_id, node_data in data.get('nodes', {}).items():
            node = Schema__MGraph__Issue__Node.from_json(node_data)
            self.graph.add_node(node)

        # Deserialize edges
        for edge_id, edge_data in data.get('edges', {}).items():
            edge = Schema__MGraph__Issue__Edge.from_json(edge_data)
            self.graph.add_edge(edge)

        self.is_loaded = True
        return True
```

---

## B20: MGraphDB Query Endpoints

### Objective

Add API endpoints that query MGraphDB.

### Endpoints

```
GET  /graph/api/nodes                    # All nodes in graph
GET  /graph/api/node/{label}             # Single node by label
GET  /graph/api/node/{label}/children    # Direct children
GET  /graph/api/node/{label}/ancestors   # Path to root
POST /graph/api/sync                     # Force resync
```

### Implementation

**File:** `routes/Routes__Graph.py` (NEW)

```python
# ═══════════════════════════════════════════════════════════════════════════════
# Routes__Graph - MGraphDB query endpoints (Phase 2)
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_fast_api.api.Fast_API__Routes                                         import Fast_API__Routes
from osbot_fast_api.api.decorators.route_path                                    import route_path
from mgraph_ai_ui_html_transformation_workbench.service.mgraph.MGraph__Issues__Sync__Service import MGraph__Issues__Sync__Service


class Routes__Graph(Fast_API__Routes):                                           # Graph query routes
    tag          : str                          = 'graph'
    sync_service : MGraph__Issues__Sync__Service

    @route_path('/graph/api/nodes')
    def list_nodes(self):                                                        # GET: All nodes
        graph = self.sync_service.ensure_loaded()
        nodes = [n.json() for n in graph.all_nodes()]
        return {'success': True, 'nodes': nodes, 'total': len(nodes)}

    @route_path('/graph/api/node/{label}')
    def get_node(self, label: str):                                              # GET: Single node
        graph = self.sync_service.ensure_loaded()
        node  = graph.get_node_by_label(label)

        if node is not None:
            return {'success': True, 'node': node.json()}

        return {'success': False, 'message': f'Node not found: {label}'}

    @route_path('/graph/api/node/{label}/children')
    def get_children(self, label: str):                                          # GET: Direct children
        graph = self.sync_service.ensure_loaded()
        node  = graph.get_node_by_label(label)

        if node is None:
            return {'success': False, 'message': f'Node not found: {label}'}

        children = graph.get_children(node.node_id)
        return {'success': True, 'nodes': [c.json() for c in children], 'total': len(children)}

    @route_path('/graph/api/node/{label}/ancestors')
    def get_ancestors(self, label: str):                                         # GET: Path to root
        graph = self.sync_service.ensure_loaded()
        node  = graph.get_node_by_label(label)

        if node is None:
            return {'success': False, 'message': f'Node not found: {label}'}

        ancestors = graph.get_ancestors(node.node_id)
        return {'success': True, 'nodes': [a.json() for a in ancestors], 'total': len(ancestors)}

    @route_path('/graph/api/sync', methods=['POST'])
    def force_sync(self):                                                        # POST: Force resync
        stats = self.sync_service.full_sync(root=self.sync_service.current_root)
        return {'success': True, 'stats': stats}
```

---

## B21: Graph Visualization Endpoints

### Objective

Return data formatted for D3/vis.js visualization.

### Endpoints

```
GET /graph/api/viz/tree?root={label}     # D3 tree format
GET /graph/api/viz/force                 # Force-directed format
```

### Response Formats

**Tree (D3 hierarchy):**
```json
{
  "name": "Project-1",
  "title": "GitGraph Issues",
  "type": "project",
  "children": [
    {
      "name": "Version-1",
      "title": "v0.1.6",
      "type": "version",
      "children": [...]
    }
  ]
}
```

**Force-directed:**
```json
{
  "nodes": [
    {"id": "Project-1", "label": "GitGraph Issues", "type": "project", "group": 1}
  ],
  "links": [
    {"source": "Project-1", "target": "Version-1", "type": "contains"}
  ]
}
```

### Implementation

**File:** `Routes__Graph.py` (add to existing)

```python
    @route_path('/graph/api/viz/tree')
    def get_viz_tree(self, root: str = None):                                    # GET: D3 tree format
        graph = self.sync_service.ensure_loaded()

        if root:
            root_node = graph.get_node_by_label(root)
        else:
            # Find node with no parent (true root)
            root_node = self.find_root_node(graph)

        if root_node is None:
            return {'success': False, 'message': 'No root found'}

        tree = self.build_tree_recursive(graph, root_node)
        return {'success': True, 'tree': tree}

    @route_path('/graph/api/viz/force')
    def get_viz_force(self):                                                     # GET: Force-directed format
        graph = self.sync_service.ensure_loaded()

        nodes = []
        links = []
        type_groups = {}
        group_counter = 0

        for node in graph.all_nodes():
            node_type = str(node.node_type)
            if node_type not in type_groups:
                type_groups[node_type] = group_counter
                group_counter += 1

            nodes.append({
                'id'   : str(node.label),
                'label': str(node.title),
                'type' : node_type,
                'group': type_groups[node_type]
            })

        for edge in graph.data.edges.values():
            source_node = graph.data.nodes.get(str(edge.source_id))
            target_node = graph.data.nodes.get(str(edge.target_id))

            if source_node and target_node:
                links.append({
                    'source': str(source_node.label),
                    'target': str(target_node.label),
                    'type'  : str(edge.edge_type)
                })

        return {'success': True, 'nodes': nodes, 'links': links}

    def find_root_node(self, graph):                                             # Find node with no parent
        all_targets = set()
        for edge in graph.data.edges.values():
            if str(edge.edge_type) == 'contains':
                all_targets.add(str(edge.target_id))

        for node_id, node in graph.data.nodes.items():
            if node_id not in all_targets:
                return node

        return None

    def build_tree_recursive(self, graph, node):                                 # Build D3 tree structure
        children      = graph.get_children(node.node_id)
        child_trees   = [self.build_tree_recursive(graph, c) for c in children]

        return {
            'name'    : str(node.label),
            'title'   : str(node.title),
            'type'    : str(node.node_type),
            'children': child_trees
        }
```

---

## B22: Hyphenated Label Support

### Objective

Generate labels like `User-Story-1` instead of `UserStory1`.

### Implementation

**File:** `Type__Service.py`

Update the label generation method:
```python
    @type_safe
    def generate_label(self                              ,                       # Generate hyphenated label
                       node_type : Safe_Str__Node_Type   ,
                       index     : int
                  ) -> Safe_Str__Node_Label:
        """
        Generate label from type and index.

        Examples:
          ('task', 1)        → 'Task-1'
          ('user-story', 5)  → 'User-Story-5'
          ('git-repo', 1)    → 'Git-Repo-1'
        """
        type_str     = str(node_type)
        words        = type_str.split('-')
        display_type = '-'.join(word.capitalize() for word in words)

        return Safe_Str__Node_Label(f"{display_type}-{index}")
```

**Also update `Node__Service.label_from_type_and_index()`:**
```python
    def label_from_type_and_index(self                              ,            # Generate hyphenated label
                                  node_type  : Safe_Str__Node_Type  ,
                                  node_index : int
                             ) -> Safe_Str__Node_Label:
        type_str     = str(node_type)
        words        = type_str.split('-')
        display_type = '-'.join(word.capitalize() for word in words)

        return Safe_Str__Node_Label(f"{display_type}-{node_index}")
```

### Backward Compatibility: Label Parsing

When parsing labels back to types (e.g., for `_resolve_link_target()`), we need to handle hyphenated types.

**Add to `Node__Service.py`:**
```python
    @type_safe
    def parse_label_to_type(self                              ,                  # Extract type from label
                            label : Safe_Str__Node_Label
                       ) -> Safe_Str__Node_Type:
        """
        Extract type from label, handling hyphenated types.

        Examples:
          'Task-1'        → 'task'
          'User-Story-5'  → 'user-story'
          'Git-Repo-1'    → 'git-repo'

        Strategy: Match against known types (longest first), then fallback.
        """
        label_str   = str(label)
        known_types = [str(nt.name) for nt in self.repository.node_types_load()]

        # Sort by length descending so 'user-story' matches before 'user'
        for node_type in sorted(known_types, key=len, reverse=True):
            prefix = self.type_to_label_prefix(node_type)

            if label_str.startswith(f"{prefix}-"):
                return Safe_Str__Node_Type(node_type)

        # Fallback: assume single-word type (first segment before hyphen)
        if '-' in label_str:
            type_part = label_str.split('-', 1)[0].lower()
            return Safe_Str__Node_Type(type_part)

        return None

    def type_to_label_prefix(self, node_type: str) -> str:                       # Convert type to label prefix
        """Convert 'user-story' → 'User-Story'."""
        return '-'.join(word.capitalize() for word in node_type.split('-'))
```

**Update `_resolve_link_target()` to use the new parser:**
```python
    def _resolve_link_target(self                           ,                    # Load target node from link
                             link : Schema__Node__Link
                        ) -> Schema__Node:
        if not link.target_label:
            return None

        target_label = Safe_Str__Node_Label(str(link.target_label))
        target_type  = self.parse_label_to_type(target_label)

        if target_type is None:
            return None

        try:
            return self.repository.node_load(node_type = target_type  ,
                                             label     = target_label )
        except Exception:
            return None
```

### Examples

| Type | Index | Label |
|------|-------|-------|
| `task` | 1 | `Task-1` |
| `user-story` | 5 | `User-Story-5` |
| `git-repo` | 1 | `Git-Repo-1` |
| `bug` | 42 | `Bug-42` |

---

## Wire-Up: FastAPI Integration

**File:** `Html_Transformation_Workbench__Fast_API.py`

### New Imports

Add these imports at the top (aligned at column 70-80):
```python
from mgraph_ai_ui_html_transformation_workbench.fast_api.routes.Routes__Graph    import Routes__Graph
from mgraph_ai_ui_html_transformation_workbench.service.mgraph.MGraph__Issues__Sync__Service import MGraph__Issues__Sync__Service
```

### New Attributes

Add to class attributes:
```python
    # Phase 2: MGraphDB services
    mgraph_sync_service : MGraph__Issues__Sync__Service = None
```

### Update setup_services()

```python
    def setup_services(self):
        # ... existing setup code ...

        # Core services - Phase 2: Node service needs root selection
        self.type_service     = Type__Service    (repository = self.graph_repository)
        self.node_service     = Node__Service    (repository             = self.graph_repository      ,
                                                  root_selection_service = self.root_selection_service)
        self.link_service     = Link__Service    (repository = self.graph_repository)
        self.comments_service = Comments__Service(repository = self.graph_repository)

        # Phase 2: MGraphDB sync service
        self.mgraph_sync_service = MGraph__Issues__Sync__Service(
            repository   = self.graph_repository,
            path_handler = self.path_handler    )

        # ... rest of existing setup ...
```

### Update setup_routes()

```python
    def setup_routes(self):
        self.add_routes(Routes__Links   , service = self.link_service          )
        self.add_routes(Routes__Nodes   , service = self.node_service          )
        self.add_routes(Routes__Types   , service = self.type_service          )
        self.add_routes(Routes__Server  , service = self.server_status_service )
        self.add_routes(Routes__Comments, service = self.comments_service      )
        self.add_routes(Routes__Roots   , service = self.root_selection_service)
        self.add_routes(Routes__Issues  , service = self.issue_children_service)
        self.add_routes(Routes__Graph   , sync_service = self.mgraph_sync_service)  # Phase 2

        self.add_routes(Routes__Info)
        self.add_routes(Routes__Set_Cookie)
```

---

## Files Summary

### New Files

```
schemas/graph/
└── Schema__Node__Info.py                # B10

mgraph/
├── Schema__MGraph__Issues.py            # B18 (pure data schemas)
└── MGraph__Issues__Domain.py            # B18 (domain operations)

services/mgraph/
└── MGraph__Issues__Sync__Service.py     # B19

routes/
└── Routes__Graph.py                     # B20, B21

scripts/
└── migrate_node_to_issue_json.py        # B13 (migration script)
```

### Modified Files

```
Graph__Repository.py                     # B10, B11, B12, B13
Node__Service.py                         # B10, B11, B14, B17, B22
Routes__Nodes.py                         # B14
Routes__Types.py                         # B15, B16
Type__Service.py                         # B15, B16, B22
Root__Selection__Service.py              # B13
Issue__Children__Service.py              # B13
Html_Transformation_Workbench__Fast_API.py
```

---

## Success Criteria

- [ ] B10: `nodes_list_all()` finds nested `issues/` folders
- [ ] B11: `node_load_by_path()` works for any path
- [ ] B12: Saving deletes legacy `node.json`
- [ ] B13: Migration script runs successfully; no `node.json` fallback
- [ ] B14: `/nodes/api/node/by-path` resolves hierarchical paths
- [ ] B15: Node types CRUD works (including PUT update)
- [ ] B16: Link types CRUD works (including PUT update)
- [ ] B17: Root scoping filters all query results
- [ ] B18: MGraph schemas follow four-layer pattern
- [ ] B19: Sync lazy loads + resyncs on root change
- [ ] B20: Graph query endpoints work
- [ ] B21: Visualization endpoints return D3/force formats
- [ ] B22: Labels like `User-Story-1` generated and parsed correctly

---

## Testing Checklist

Before merging, verify:

1. **Type Safety:** All new code passes `@type_safe` validation
2. **No Regressions:** Existing tests pass
3. **Migration:** Run `migrate_node_to_issue_json.py --dry-run` first
4. **Integration:** Full stack works with UI

---

*Backend Implementation Brief v2.0 (Revised)*  
*Project: GitGraph Issues Phase 2*  
*Tasks: B10-B22*  
*Date: 2026-02-03*
