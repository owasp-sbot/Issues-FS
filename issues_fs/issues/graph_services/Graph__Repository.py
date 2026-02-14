# ═══════════════════════════════════════════════════════════════════════════════
# Graph__Repository - Memory-FS based data access for graph nodes
# Storage-agnostic: works with Memory, Local Disk, S3, SQLite, ZIP backends
#
# Phase 1 Changes:
#   - node_load: Reads issue.json first, falls back to node.json
#   - node_save: Always writes to issue.json (preserves node.json for now)
#   - node_exists: Checks for either issue.json or node.json
#
# Phase 2 Changes:
#   - B10: nodes_list_all() for recursive discovery in issues/ folders
#   - B11: node_load_by_path(), node_find_path_by_label() for path-based loading
#   - B12: node_save() now deletes legacy node.json after saving
#   - B13: get_issue_file_path() no longer falls back to node.json
#
# .issues File Integration:
#   - issues_files_discover(): finds *.issues files in storage
#   - issues_files_load(): parses .issues files into Schema__Node list
#   - nodes_list_all(): now includes nodes from .issues files
#   - node_load_by_label(): searches .issues-sourced nodes too
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                             import List, Optional
from memory_fs.Memory_FS                                                                                import Memory_FS
from memory_fs.storage_fs.Storage_FS                                                                    import Storage_FS
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                       import Safe_Str__File__Path
from osbot_utils.utils.Json                                                                             import json_loads, json_dumps
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                      import Safe_Str__Node_Type, Safe_Str__Node_Label
from issues_fs.schemas.graph.Schema__Global__Index                                                      import Schema__Global__Index
from issues_fs.schemas.graph.Schema__Node                                                               import Schema__Node
from issues_fs.schemas.graph.Schema__Node__Info                                                         import Schema__Node__Info
from issues_fs.schemas.graph.Schema__Node__Type                                                         import Schema__Node__Type
from issues_fs.schemas.graph.Schema__Link__Type                                                         import Schema__Link__Type
from issues_fs.schemas.graph.Schema__Type__Index                                                        import Schema__Type__Index
from issues_fs.issues.storage.Path__Handler__Graph_Node                                                 import Path__Handler__Graph_Node
from issues_fs.issues.issues_file.Issues_File__Loader__Service                                          import Issues_File__Loader__Service

# todo: find a better way to do this
SKIP_LABELS  = {'config', 'data', 'issues', 'indexes', '.issues'}                # Phase 2: System folder names

class Graph__Repository(Type_Safe):                                              # Memory-FS based graph repository
    memory_fs            : Memory_FS                                             # Storage abstraction
    path_handler         : Path__Handler__Graph_Node                             # Path generation
    storage_fs           : Storage_FS             = None                         # Set from memory_fs
    issues_file_loader   : Issues_File__Loader__Service  = None                  # .issues file loader
    issues_file_nodes    : list                          = None                  # cached nodes from .issues files
    issues_file_loaded   : bool                          = False                 # whether cache is populated

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.memory_fs:
            self.storage_fs = self.memory_fs.storage_fs

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Operations - Phase 2: Save with Legacy Cleanup
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def node_save(self, node: Schema__Node) -> bool:                             # Save node to issue.json
        if not node.label:
            return False

        path_issue = self.path_handler.path_for_issue_json(node_type = node.node_type,
                                                           label     = node.label    )
        data       = node.json()
        content    = json_dumps(data, indent=2)
        result     = self.storage_fs.file__save(path_issue, content.encode('utf-8'))

        if result is True:                                                       # Phase 2 (B12): Delete legacy file
            self.delete_legacy_node_json(node.node_type, node.label)

        return result

    @type_safe
    def delete_legacy_node_json(self                              ,              # Phase 2 (B12): Remove legacy node.json
                                node_type : Safe_Str__Node_Type   ,
                                label     : Safe_Str__Node_Label
                           ) -> bool:
        path_node = self.path_handler.path_for_node_json(node_type, label)

        if self.storage_fs.file__exists(path_node) is True:
            return self.storage_fs.file__delete(path_node)

        return False

    @type_safe
    def node_load(self                              ,                            # Load node by type and label
                  node_type : Safe_Str__Node_Type   ,
                  label     : Safe_Str__Node_Label
             ) -> Schema__Node:
        path = self.get_issue_file_path(node_type, label)
        if path is None:
            return None

        content = self.storage_fs.file__str(path)
        if not content:
            return None

        data = json_loads(content)
        if data is None:
            return None

        return Schema__Node.from_json(data)

    @type_safe
    def node_delete(self                              ,                          # Delete node from storage
                    node_type : Safe_Str__Node_Type   ,
                    label     : Safe_Str__Node_Label
               ) -> bool:
        deleted_any  = False
        path_issue   = self.path_handler.path_for_issue_json(node_type, label)
        path_node    = self.path_handler.path_for_node_json(node_type, label)

        if self.storage_fs.file__exists(path_issue):
            self.storage_fs.file__delete(path_issue)
            deleted_any = True

        if self.storage_fs.file__exists(path_node):                              # Also delete legacy node.json
            self.storage_fs.file__delete(path_node)
            deleted_any = True

        return deleted_any

    @type_safe
    def node_exists(self                              ,                          # Check if node exists
                    node_type : Safe_Str__Node_Type   ,
                    label     : Safe_Str__Node_Label
               ) -> bool:
        return self.get_issue_file_path(node_type, label) is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # File Path Resolution - Phase 2: issue.json Only (B13)
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def get_issue_file_path(self                              ,                  # Get issue file path (issue.json only)
                            node_type : Safe_Str__Node_Type   ,
                            label     : Safe_Str__Node_Label
                       ) -> Safe_Str__File__Path:
        path_issue = self.path_handler.path_for_issue_json(node_type, label)

        if self.storage_fs.file__exists(path_issue) is True:
            return path_issue

        return None                                                              # Phase 2 (B13): No node.json fallback

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Discovery - Phase 2 (B10): Recursive Search
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def nodes_list_all(self                                    ,                 # Find all issues recursively
                       root_path      : Safe_Str__File__Path = None ,
                       include_issues_files : bool           = True
                  ) -> List[Schema__Node__Info]:
        all_paths = self.storage_fs.files__paths()
        nodes     = []
        seen_labels = set()

        for path in all_paths:
            if path.endswith('/issue.json') is False:                            # Only issue.json files
                continue

            if root_path is not None and str(root_path) != '':                   # Filter by root if specified
                if self.is_path_under_root(path, root_path) is False:
                    continue

            folder_path = path.rsplit('/issue.json', 1)[0]                       # Extract folder path
            label       = folder_path.rsplit('/', 1)[-1]                         # Extract label from path

            if label in SKIP_LABELS:                                             # Skip system folders
                continue

            node_type = self.extract_node_type_from_file(path)

            node_info = Schema__Node__Info(label     = label      ,
                                           path      = folder_path,
                                           node_type = node_type  )
            nodes.append(node_info)
            seen_labels.add(label)

        if include_issues_files is True:                                         # Add nodes from .issues files
            for node in self.issues_files_get_cached_nodes():
                label = str(node.label)
                if label not in seen_labels:                                     # JSON nodes take precedence
                    node_info = Schema__Node__Info(label     = label             ,
                                                   path      = f'.issues/{label}',
                                                   node_type = str(node.node_type))
                    nodes.append(node_info)
                    seen_labels.add(label)

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
    def extract_node_type_from_file(self                              ,          # Get node_type from JSON file
                                    file_path : Safe_Str__File__Path
                               ) -> Safe_Str__Node_Type:
        try:
            content = self.storage_fs.file__str(str(file_path))
            if content:
                data = json_loads(content)
                return data.get('node_type', '')
        except (ValueError, KeyError):                                           # JSON parse or key errors
            pass
        return ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Loading - Phase 2 (B11): Path-Based Access
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def node_load_by_path(self                              ,                    # Load by explicit folder path
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
                return folder_path

        return None

    @type_safe
    def node_load_by_label(self                              ,                   # Load by label (recursive search)
                           label : Safe_Str__Node_Label
                      ) -> Schema__Node:
        path = self.node_find_path_by_label(label)

        if path is not None:
            return self.node_load_by_path(path)

        issues_node = self.issues_files_find_node_by_label(str(label))           # Fall back to .issues files
        if issues_node is not None:
            return issues_node

        return None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Listing Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def nodes_list_labels(self                                    ,              # List all node labels for type
                          node_type : Safe_Str__Node_Type = None
                     ) -> List[Safe_Str__Node_Label]:
        all_nodes = self.nodes_list_all()                                        # Phase 2: Use recursive discovery

        if node_type is not None:
            type_str = str(node_type)
            return [n.label for n in all_nodes if str(n.node_type) == type_str]

        return [n.label for n in all_nodes]

    # ═══════════════════════════════════════════════════════════════════════════════
    # Type Index Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def type_index_load(self                              ,                      # Load per-type index
                        node_type : Safe_Str__Node_Type
                   ) -> Schema__Type__Index:
        path = self.path_handler.path_for_type_index(node_type)
        if self.storage_fs.file__exists(path) is False:
            return Schema__Type__Index(node_type=node_type)

        content = self.storage_fs.file__str(path)
        if not content:
            return Schema__Type__Index(node_type=node_type)

        data = json_loads(content)
        if data is None:
            return Schema__Type__Index(node_type=node_type)

        return Schema__Type__Index.from_json(data)

    @type_safe
    def type_index_save(self                              ,                      # Save per-type index
                        index : Schema__Type__Index
                   ) -> bool:
        path    = self.path_handler.path_for_type_index(index.node_type)
        data    = index.json()
        content = json_dumps(data, indent=2)
        return self.storage_fs.file__save(path, content.encode('utf-8'))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Global Index Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def global_index_load(self) -> Schema__Global__Index:                        # Load global index
        path = self.path_handler.path_for_global_index()
        if self.storage_fs.file__exists(path) is False:
            return Schema__Global__Index()

        content = self.storage_fs.file__str(path)
        if not content:
            return Schema__Global__Index()

        data = json_loads(content)
        if data is None:
            return Schema__Global__Index()

        return Schema__Global__Index.from_json(data)

    def global_index_save(self, index: Schema__Global__Index) -> bool:           # Save global index
        path    = self.path_handler.path_for_global_index()
        data    = index.json()
        content = json_dumps(data, indent=2)
        return self.storage_fs.file__save(path, content.encode('utf-8'))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Config Operations - Node Types
    # ═══════════════════════════════════════════════════════════════════════════════

    def node_types_load(self) -> List[Schema__Node__Type]:                       # Load all node types
        path = self.path_handler.path_for_node_types()
        if self.storage_fs.file__exists(path) is False:
            return []

        content = self.storage_fs.file__str(path)
        if not content:
            return []

        data = json_loads(content)
        if data is None or 'types' not in data:
            return []

        types = []
        for item in data['types']:
            types.append(Schema__Node__Type.from_json(item))
        return types

    def node_types_save(self, types: List[Schema__Node__Type]) -> bool:          # Save all node types
        path = self.path_handler.path_for_node_types()
        data = {'types': [t.json() for t in types]}
        content = json_dumps(data, indent=2)
        return self.storage_fs.file__save(path, content.encode('utf-8'))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Config Operations - Link Types
    # ═══════════════════════════════════════════════════════════════════════════════

    def link_types_load(self) -> List[Schema__Link__Type]:                       # Load all link types
        path = self.path_handler.path_for_link_types()
        if self.storage_fs.file__exists(path) is False:
            return []

        content = self.storage_fs.file__str(path)
        if not content:
            return []

        data = json_loads(content)
        if data is None or 'link_types' not in data:
            return []

        types = []
        for item in data['link_types']:
            types.append(Schema__Link__Type.from_json(item))
        return types

    def link_types_save(self, types: List[Schema__Link__Type]) -> bool:          # Save all link types
        path = self.path_handler.path_for_link_types()
        data = {'link_types': [t.json() for t in types]}
        content = json_dumps(data, indent=2)
        return self.storage_fs.file__save(path, content.encode('utf-8'))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Attachment Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def attachment_save(self                              ,                      # Save attachment (raw bytes)
                        node_type : Safe_Str__Node_Type   ,
                        label     : Safe_Str__Node_Label  ,
                        filename  : str                   ,
                        data      : bytes
                   ) -> bool:
        path = self.path_handler.path_for_attachment(node_type = node_type ,
                                                     label     = label     ,
                                                     filename  = filename  )
        return self.storage_fs.file__save(path, data)

    @type_safe
    def attachment_load(self                              ,                      # Load attachment
                        node_type : Safe_Str__Node_Type   ,
                        label     : Safe_Str__Node_Label  ,
                        filename  : str
                   ) -> bytes:
        path = self.path_handler.path_for_attachment(node_type = node_type ,
                                                     label     = label     ,
                                                     filename  = filename  )
        if self.storage_fs.file__exists(path) is False:
            return None
        return self.storage_fs.file__bytes(path)

    @type_safe
    def attachment_delete(self                              ,                    # Delete attachment
                          node_type : Safe_Str__Node_Type   ,
                          label     : Safe_Str__Node_Label  ,
                          filename  : str
                     ) -> bool:
        path = self.path_handler.path_for_attachment(node_type = node_type ,
                                                     label     = label     ,
                                                     filename  = filename  )
        if self.storage_fs.file__exists(path):
            return self.storage_fs.file__delete(path)
        return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # .issues File Integration
    # ═══════════════════════════════════════════════════════════════════════════════

    def issues_files_discover(self) -> List[str]:                                # Find all *.issues files in storage
        all_paths = self.storage_fs.files__paths()
        return [str(p) for p in all_paths if str(p).endswith('.issues')]

    def issues_files_load(self) -> list:                                         # Parse .issues files into Schema__Node
        if self.issues_file_loader is None:
            self.issues_file_loader = Issues_File__Loader__Service()

        issues_paths = self.issues_files_discover()
        if not issues_paths:
            self.issues_file_nodes  = []
            self.issues_file_loaded = True
            return []

        files = []
        for path in issues_paths:
            content = self.storage_fs.file__str(path)
            if content:
                files.append((content, str(path)))

        result = self.issues_file_loader.load_multiple(files)
        self.issues_file_nodes  = result.nodes
        self.issues_file_loaded = True
        return result.nodes

    def issues_files_get_cached_nodes(self) -> list:                             # Get cached .issues nodes (load if needed)
        if self.issues_file_loaded is False:
            self.issues_files_load()
        return self.issues_file_nodes or []

    def issues_files_find_node_by_label(self, label: str):                       # Find a node from .issues files by label
        for node in self.issues_files_get_cached_nodes():
            if str(node.label) == label:
                return node
        return None

    def issues_files_invalidate_cache(self):                                     # Clear cached .issues nodes (force reload)
        self.issues_file_loaded = False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Utility Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def clear_storage(self) -> None:                                             # Clear all data (for tests)
        self.storage_fs.clear()
        self.issues_file_loaded = False
