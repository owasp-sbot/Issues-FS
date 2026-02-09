# ═══════════════════════════════════════════════════════════════════════════════
# Issue__Children__Service - Service for managing child issues in issues/ folders
# Phase 1: Enables adding children to issues and converting to hierarchical structure
# Phase 2 (B13): Removed node.json fallback - issue.json only
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
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types                     import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node                              import Schema__Node
from mgraph_ai_ui_html_transformation_workbench.schemas.issues.phase_1.Schema__Issue__Children          import Schema__Issue__Child__Create, Schema__Issue__Child__Response, Schema__Issue__Convert__Response, Schema__Issue__Children__List__Response
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository         import Graph__Repository
from mgraph_ai_ui_html_transformation_workbench.service.issues.storage.Path__Handler__Graph_Node        import Path__Handler__Graph_Node, FILE_NAME__ISSUE_JSON


class Issue__Children__Service(Type_Safe):                                       # Service for child issue management
    repository   : Graph__Repository                                             # Data access layer
    path_handler : Path__Handler__Graph_Node                                     # Path generation

    # ═══════════════════════════════════════════════════════════════════════════════
    # Add Child Issue
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def add_child_issue(self                                            ,        # Add child issue to parent
                        parent_path : Safe_Str__File__Path              ,
                        child_data  : Schema__Issue__Child__Create
                   ) -> Schema__Issue__Child__Response:
        full_parent_path = self.resolve_full_path(str(parent_path))

        if self.parent_exists(full_parent_path) is False:
            return Schema__Issue__Child__Response(success = False                                  ,
                                                  message = f'Parent not found: {parent_path}'    )

        issues_folder = f"{full_parent_path}/issues"
        self.ensure_folder_exists(issues_folder)

        child_type  = str(child_data.issue_type)
        child_label = self.generate_child_label(issues_folder, child_type)

        child_folder = f"{issues_folder}/{child_label}"
        self.ensure_folder_exists(child_folder)

        now = Timestamp_Now()
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

        child_path = f"{child_folder}/{FILE_NAME__ISSUE_JSON}"
        data       = child_issue.json()
        content    = json_dumps(data, indent=2)
        saved      = self.repository.storage_fs.file__save(child_path, content.encode('utf-8'))

        if saved is False:
            return Schema__Issue__Child__Response(success = False                          ,
                                                  message = 'Failed to save child issue'   )

        relative_child_path = self.make_relative_path(child_folder)

        return Schema__Issue__Child__Response(success     = True                ,
                                              path        = relative_child_path ,
                                              label       = child_label         ,
                                              issue_type  = child_type          ,
                                              title       = str(child_data.title))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Convert to New Structure
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def convert_to_new_structure(self                            ,
                                 issue_path : Safe_Str__File__Path
                            ) -> Schema__Issue__Convert__Response:
        full_path = self.resolve_full_path(str(issue_path))

        if self.parent_exists(full_path) is False:
            return Schema__Issue__Convert__Response(success = False                             ,
                                                    message = f'Issue not found: {issue_path}'  )

        issues_folder = f"{full_path}/issues"

        if self.folder_exists(issues_folder):
            return Schema__Issue__Convert__Response(success      = True                             ,
                                                    converted    = False                            ,
                                                    issues_path  = self.make_relative_path(issues_folder),
                                                    message      = 'Already has issues/ folder'     )

        self.ensure_folder_exists(issues_folder)

        placeholder_path = f"{issues_folder}/.gitkeep"
        self.repository.storage_fs.file__save(placeholder_path, b'')

        return Schema__Issue__Convert__Response(success     = True                                   ,
                                                converted   = True                                   ,
                                                issues_path = self.make_relative_path(issues_folder) ,
                                                message     = 'Created issues/ folder'               )

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Children
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def list_children(self                            ,
                      parent_path : Safe_Str__File__Path
                 ) -> Schema__Issue__Children__List__Response:
        full_path     = self.resolve_full_path(str(parent_path))
        issues_folder = f"{full_path}/issues"

        if self.folder_exists(issues_folder) is False:
            return Schema__Issue__Children__List__Response(success  = True   ,
                                                           children = []     ,
                                                           total    = Safe_UInt(0))

        child_folders = self.scan_child_folders(Safe_Str__File__Path(issues_folder))
        children      = []

        for child_folder in child_folders:
            summary = self.load_child_summary(Safe_Str__File__Path(child_folder))
            if summary:
                children.append(summary)

        return Schema__Issue__Children__List__Response(success  = True                    ,
                                                       children = children                ,
                                                       total    = Safe_UInt(len(children)))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Path Resolution
    # ═══════════════════════════════════════════════════════════════════════════════

    def resolve_full_path(self, path: str) -> str:
        if not path:
            base_path = str(self.path_handler.base_path)
            return base_path if base_path and base_path != '.' else ''

        base_path = str(self.path_handler.base_path)

        if base_path and base_path != '.':
            if path.startswith(base_path):
                return path
            return f"{base_path}/{path}"

        return path

    def make_relative_path(self, full_path: str) -> str:
        base_path = str(self.path_handler.base_path)

        if base_path and base_path != '.':
            prefix = f"{base_path}/"
            if full_path.startswith(prefix):
                return full_path[len(prefix):]

        return full_path

    # ═══════════════════════════════════════════════════════════════════════════════
    # Existence Checks - Phase 2 (B13): issue.json only
    # ═══════════════════════════════════════════════════════════════════════════════

    def parent_exists(self, folder_path: str) -> bool:                           # Check if parent issue exists
        issue_path = f"{folder_path}/{FILE_NAME__ISSUE_JSON}"
        return self.repository.storage_fs.file__exists(issue_path)               # Phase 2: issue.json only

    def folder_exists(self, folder_path: str) -> bool:
        all_paths = self.repository.storage_fs.files__paths()
        prefix    = f"{folder_path}/"

        for path in all_paths:
            if path.startswith(prefix):
                return True

        return False

    def ensure_folder_exists(self, folder_path: str) -> None:
        pass                                                                     # Memory-FS creates folders implicitly

    @type_safe
    def scan_child_folders(self                              ,                   # Find all child folders in issues/
                           issues_folder : Safe_Str__File__Path
                      ) -> List[str]:
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

    # ═══════════════════════════════════════════════════════════════════════════════
    # Label Generation
    # ═══════════════════════════════════════════════════════════════════════════════

    def generate_child_label(self                     ,
                             issues_folder : str      ,
                             child_type    : str
                        ) -> str:
        existing_indices = self.get_existing_indices(Safe_Str__File__Path(issues_folder), child_type)

        next_index = 1
        if existing_indices:
            next_index = max(existing_indices) + 1

        display_type = child_type.capitalize()

        if '-' in child_type:                                                    # Phase 2 (B22): Hyphenated labels
            parts = child_type.split('-')
            display_type = '-'.join(p.capitalize() for p in parts)

        return f"{display_type}-{next_index}"

    def get_existing_indices(self                              ,
                             issues_folder : Safe_Str__File__Path ,
                             child_type    : str
                        ) -> List[int]:
        indices   = []
        all_paths = self.repository.storage_fs.files__paths()
        prefix    = f"{issues_folder}/"

        display_type = child_type.capitalize()
        if '-' in child_type:
            parts = child_type.split('-')
            display_type = '-'.join(p.capitalize() for p in parts)

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

    def extract_index_from_label(self, label: str) -> Safe_UInt:
        if '-' in label:
            try:
                index_str = label.rsplit('-', 1)[1]
                return Safe_UInt(int(index_str))
            except (ValueError, IndexError):
                pass
        return Safe_UInt(1)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Child Data Loading - Phase 2 (B13): issue.json only
    # ═══════════════════════════════════════════════════════════════════════════════

    def load_child_summary(self                              ,
                           child_folder : Safe_Str__File__Path
                      ) -> dict:
        issue_path = f"{child_folder}/{FILE_NAME__ISSUE_JSON}"
        data       = self.load_issue_from_path(Safe_Str__File__Path(issue_path))

        if data:
            data['path'] = self.make_relative_path(str(child_folder))
            return data

        return None                                                              # Phase 2: No node.json fallback

    def load_issue_from_path(self                              ,
                             file_path : Safe_Str__File__Path
                        ) -> dict:
        if self.repository.storage_fs.file__exists(str(file_path)) is False:
            return None

        content = self.repository.storage_fs.file__str(str(file_path))
        if not content:
            return None

        return json_loads(content)
