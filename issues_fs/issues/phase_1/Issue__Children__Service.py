# ═══════════════════════════════════════════════════════════════════════════════
# Issue__Children__Service - Service for managing child issues in issues/ folders
# Phase 1: Enables adding children to issues and converting to hierarchical structure
#
# Key Operations:
#   - add_child_issue: Create a child issue in parent's issues/ folder
#   - convert_to_new_structure: Create issues/ folder for an existing issue
#   - list_children: List all children in an issue's issues/ folder
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                             import List
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                       import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                       import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                        import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                        import Timestamp_Now
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
from osbot_utils.utils.Json                                                                             import json_dumps, json_loads
from issues_fs.schemas.graph.Safe_Str__Graph_Types                     import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status
from issues_fs.schemas.graph.Schema__Node                              import Schema__Node
from issues_fs.schemas.issues.phase_1.Schema__Issue__Children          import Schema__Issue__Child__Create, Schema__Issue__Child__Response, Schema__Issue__Convert__Response, Schema__Issue__Children__List__Response
from issues_fs.issues.graph_services.Graph__Repository         import Graph__Repository
from issues_fs.issues.storage.Path__Handler__Graph_Node        import Path__Handler__Graph_Node, FILE_NAME__ISSUE_JSON


# todo: fix casting to types (like str(..) ) , which is not needed since Type_Safe handles that well (as long are we go into a Type_Safe class, primitive of decorator)
#       create vulns for path transversal issues (i.e. all places where are are doing a path combine using strings
#            see how we can make this work with the Safe_Str__File__Path , for example using the same trick with "/" that Path uses
#            we could use this to create a variation of Safe_Str__File__Path that did not supported path transversal attacks

class Issue__Children__Service(Type_Safe):                                       # Service for child issue management
    repository   : Graph__Repository                                             # Data access layer
    path_handler : Path__Handler__Graph_Node                                     # Path generation

    # ═══════════════════════════════════════════════════════════════════════════════
    # Add Child Issue
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def add_child_issue(self                                            ,        # Add child issue to parent
                        parent_path : Safe_Str__File__Path                    ,  # Path to parent (relative or full)
                        child_data  : Schema__Issue__Child__Create
                   ) -> Schema__Issue__Child__Response:
        full_parent_path = self.resolve_full_path(str(parent_path))              # Resolve parent path

        if self.parent_exists(full_parent_path) is False:                        # Validate parent exists
            return Schema__Issue__Child__Response(success = False                                  ,
                                                  message = f'Parent not found: {parent_path}'    )

        issues_folder = f"{full_parent_path}/issues"                             # Ensure issues/ folder exists
        self.ensure_folder_exists(issues_folder)

        child_type  = str(child_data.issue_type)                                 # Generate label for child
        child_label = self.generate_child_label(issues_folder, child_type)

        child_folder = f"{issues_folder}/{child_label}"                          # Create child folder
        self.ensure_folder_exists(child_folder)

        now = Timestamp_Now()                                                    # Create child issue
        child_issue = Schema__Node(node_id     = Node_Id()                                      ,
                                   node_type   = Safe_Str__Node_Type(child_type)                ,
                                   node_index  = self.extract_index_from_label(child_label)     ,
                                   label       = Safe_Str__Node_Label(child_label)              ,
                                   title       = str(child_data.title)                          ,
                                   description = str(child_data.description) if child_data.description else '',
                                   status      = Safe_Str__Status(str(child_data.status)) if child_data.status else Safe_Str__Status('backlog'),
                                   created_at  = now                                            ,
                                   updated_at  = now                                            ,
                                   created_by  = Obj_Id()                                       ,
                                   tags        = []                                             ,
                                   links       = []                                             ,
                                   properties  = {}                                             )

        child_path = f"{child_folder}/{FILE_NAME__ISSUE_JSON}"                   # Save child issue
        data       = child_issue.json()
        content    = json_dumps(data, indent=2)
        saved      = self.repository.storage_fs.file__save(child_path, content.encode('utf-8'))

        if saved is False:
            return Schema__Issue__Child__Response(success = False                          ,
                                                  message = 'Failed to save child issue'   )

        relative_child_path = self.make_relative_path(child_folder)              # Calculate relative path for response

        return Schema__Issue__Child__Response(success     = True                ,
                                              path        = relative_child_path ,
                                              label       = child_label         ,
                                              issue_type  = child_type          ,
                                              title       = str(child_data.title))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Convert to New Structure
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def convert_to_new_structure(self                            ,               # Create issues/ folder for issue
                                 issue_path : Safe_Str__File__Path
                            ) -> Schema__Issue__Convert__Response:
        full_path = self.resolve_full_path(str(issue_path))

        if self.parent_exists(full_path) is False:                               # Validate issue exists
            return Schema__Issue__Convert__Response(success = False                             ,
                                                    message = f'Issue not found: {issue_path}'  )

        issues_folder = f"{full_path}/issues"

        if self.folder_exists(issues_folder):                                    # Check if already converted
            return Schema__Issue__Convert__Response(success      = True                             ,
                                                    converted    = False                            ,
                                                    issues_path  = self.make_relative_path(issues_folder),
                                                    message      = 'Already has issues/ folder'     )

        self.ensure_folder_exists(issues_folder)                                 # Create the issues/ folder

        placeholder_path = f"{issues_folder}/.gitkeep"                           # Create placeholder to ensure folder persists
        self.repository.storage_fs.file__save(placeholder_path, b'')

        return Schema__Issue__Convert__Response(success     = True                                   ,
                                                converted   = True                                   ,
                                                issues_path = self.make_relative_path(issues_folder) ,
                                                message     = 'Created issues/ folder'               )

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Children
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def list_children(self                            ,                          # List children in issues/ folder
                      parent_path : Safe_Str__File__Path
                 ) -> Schema__Issue__Children__List__Response:
        full_path     = self.resolve_full_path(str(parent_path))
        issues_folder = f"{full_path}/issues"

        if self.folder_exists(issues_folder) is False:                           # Check if issues/ folder exists
            return Schema__Issue__Children__List__Response(success  = True   ,
                                                           children = []     ,
                                                           total    = Safe_UInt(0))

        children = []
        child_folders = self.scan_child_folders(issues_folder)                   # Scan for child issue folders

        for child_folder in sorted(child_folders):
            child_data = self.load_child_summary(child_folder)
            if child_data:
                children.append(child_data)

        return Schema__Issue__Children__List__Response(success  = True              ,
                                                       children = children          ,
                                                       total    = Safe_UInt(len(children)))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Path Resolution Helpers
    # ═══════════════════════════════════════════════════════════════════════════════

    def resolve_full_path(self, path: str) -> str:                               # Convert relative path to full path
        if not path:
            base_path = str(self.path_handler.base_path)
            if base_path and base_path != '.':
                return base_path
            return ''                                                            # Empty base_path = root is ''

        base_path = str(self.path_handler.base_path)

        if not base_path or base_path == '.':                                    # No base_path, path is already relative to storage root
            return path

        if path.startswith(base_path):
            return path

        return f"{base_path}/{path}"

    def make_relative_path(self, full_path: str) -> str:                         # Convert full path to relative
        base_path = str(self.path_handler.base_path)

        if not base_path or base_path == '.':                                    # No base_path, path is already relative
            return full_path

        prefix = f"{base_path}/"
        if full_path.startswith(prefix):
            return full_path[len(prefix):]

        return full_path

    # ═══════════════════════════════════════════════════════════════════════════════
    # Folder Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def parent_exists(self, folder_path: str) -> bool:                           # Check if parent issue exists
        issue_json = f"{folder_path}/{FILE_NAME__ISSUE_JSON}" if folder_path else FILE_NAME__ISSUE_JSON
        node_json  = f"{folder_path}/node.json" if folder_path else "node.json"

        if self.repository.storage_fs.file__exists(issue_json):
            return True
        if self.repository.storage_fs.file__exists(node_json):
            return True

        base_path = str(self.path_handler.base_path)                             # Root is always valid parent
        if not folder_path or folder_path == base_path or folder_path == '.' or folder_path == '':
            return True

        return False

    def folder_exists(self, folder_path: str) -> bool:                           # Check if folder exists (has any files)
        all_paths = self.repository.storage_fs.files__paths()
        prefix    = f"{folder_path}/"

        for path in all_paths:
            if path.startswith(prefix):
                return True

        return False

    def ensure_folder_exists(self, folder_path: str) -> None:                           # Ensure folder exists in storage
        # todo: see if we need this method
        #       if we do add the logic to create the folder when not in memory
        #       if we don't  need it delete this method
        pass                                                                            # Memory-FS creates folders implicitly

    @type_safe
    def scan_child_folders(self,                                                        # Find all child folders in issues/
                           issues_folder: Safe_Str__File__Path
                      ) -> List[Safe_Str__File__Path]:
        folders   = set()
        all_paths = self.repository.storage_fs.files__paths()
        prefix    = f"{issues_folder}/"

        for path in all_paths:
            if path.startswith(prefix) is False:
                continue

            relative = path[len(prefix):]                                        # Remove prefix
            parts    = relative.split('/')

            if len(parts) >= 2:
                child_folder = parts[0]                                          # First segment is child folder
                filename     = parts[1]

                if filename in (FILE_NAME__ISSUE_JSON, 'node.json'):
                    folders.add(f"{issues_folder}/{child_folder}")

        return folders

    # ═══════════════════════════════════════════════════════════════════════════════
    # Label Generation
    # ═══════════════════════════════════════════════════════════════════════════════

    def generate_child_label(self                     ,                          # Generate label for new child
                             issues_folder : Safe_Str__File__Path      ,
                             child_type    : str
                        ) -> str:
        existing_indices = self.get_existing_indices(issues_folder, child_type)  # Find highest existing index

        next_index = 1
        if existing_indices:
            next_index = max(existing_indices) + 1

        display_type = child_type.capitalize()                                   # Generate label: "Task" + "-" + "1"

        if '-' in child_type:                                                    # Handle types like "git-repo"
            parts = child_type.split('-')
            display_type = ''.join(p.capitalize() for p in parts)

        return f"{display_type}-{next_index}"

    # todo: these str should be type_safe primitives
    def get_existing_indices(self                     ,                          # Get all existing indices for type
                             issues_folder : Safe_Str__File__Path      ,
                             child_type    : str
                        ) -> List[int]:
        indices   = []
        all_paths = self.repository.storage_fs.files__paths()
        prefix    = f"{issues_folder}/"

        display_type = child_type.capitalize()
        if '-' in child_type:
            parts = child_type.split('-')
            display_type = ''.join(p.capitalize() for p in parts)

        label_prefix = f"{display_type}-"

        for path in all_paths:
            if path.startswith(prefix) is False:
                continue

            relative = path[len(prefix):]
            parts    = relative.split('/')

            if len(parts) >= 1:
                folder_name = parts[0]

                if folder_name.startswith(label_prefix):
                    try:
                        index_str = folder_name[len(label_prefix):]
                        index     = int(index_str)
                        indices.append(index)
                    except ValueError:
                        pass

        return indices

    def extract_index_from_label(self, label: str) -> Safe_UInt:                 # Extract index number from label
        if '-' in label:
            try:
                index_str = label.rsplit('-', 1)[1]
                return Safe_UInt(int(index_str))
            except (ValueError, IndexError):
                pass
        return Safe_UInt(1)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Child Data Loading
    # ═══════════════════════════════════════════════════════════════════════════════

    # todo: this should not be a raw dict
    def load_child_summary(self, child_folder: Safe_Str__File__Path) -> dict:                     # Load summary data for child
        issue_path = f"{child_folder}/{FILE_NAME__ISSUE_JSON}"                   # Try issue.json first
        data = self.load_issue_from_path(issue_path)
        if data:
            data['path'] = self.make_relative_path(child_folder)
            return data

        node_path = f"{child_folder}/node.json"                                  # Fall back to node.json
        data = self.load_issue_from_path(node_path)
        if data:
            data['path'] = self.make_relative_path(child_folder)
            return data

        return None

    # todo: this should not be a raw dict
    def load_issue_from_path(self, file_path: Safe_Str__File__Path) -> dict:                      # Load issue JSON from path
        if self.repository.storage_fs.file__exists(file_path) is False:
            return None

        content = self.repository.storage_fs.file__str(file_path)
        if not content:
            return None

        return json_loads(content)