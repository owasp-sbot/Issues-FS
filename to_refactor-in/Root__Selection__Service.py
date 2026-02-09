# ═══════════════════════════════════════════════════════════════════════════════
# Root__Selection__Service - Service for managing which folder is the current root
# Phase 1: Enables selecting any folder with issue.json/node.json as the root
# Phase 2 (B13): Removed node.json fallback - issue.json only
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                             import List
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                       import Safe_Str__File__Path
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
from osbot_utils.utils.Json                                                                             import json_loads
from mgraph_ai_ui_html_transformation_workbench.schemas.issues.phase_1.Schema__Root                     import Schema__Root__Candidate, Schema__Root__List__Response, Schema__Root__Current__Response, Schema__Root__Select__Response, Schema__Root__Select__Request
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository         import Graph__Repository
from mgraph_ai_ui_html_transformation_workbench.service.issues.storage.Path__Handler__Graph_Node        import Path__Handler__Graph_Node, FILE_NAME__ISSUE_JSON


class Root__Selection__Service(Type_Safe):                                       # Service for root folder selection
    repository   : Graph__Repository                                             # Data access layer
    path_handler : Path__Handler__Graph_Node                                     # Path generation
    current_root : Safe_Str__File__Path                                          # Currently selected root path

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Available Roots
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_available_roots(self) -> Schema__Root__List__Response:               # Find all folders that could serve as roots
        candidates = []

        root_candidate = self.create_issues_root_candidate()                     # The .issues/ folder itself is always first
        candidates.append(root_candidate)

        issue_folders = self.scan_for_issue_folders()                            # Find all folders with issue.json
        for folder_path in sorted(issue_folders):
            candidate = self.create_candidate_from_folder(folder_path)
            if candidate:
                candidates.append(candidate)

        return Schema__Root__List__Response(success = True            ,
                                            roots   = candidates      ,
                                            total   = Safe_UInt(len(candidates)))

    def get_roots_with_children(self) -> Schema__Root__List__Response:           # Get only roots that have issues/ folders
        all_roots = self.get_available_roots()

        if all_roots.success is False:
            return all_roots

        roots_with_children = [r for r in all_roots.roots if r.has_issues is True]

        return Schema__Root__List__Response(success = True                           ,
                                            roots   = roots_with_children            ,
                                            total   = Safe_UInt(len(roots_with_children)))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get/Set Current Root
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_current_root(self) -> Schema__Root__Current__Response:               # Get currently selected root
        if not self.current_root:
            return Schema__Root__Current__Response(success    = True            ,
                                                   path       = ''              ,
                                                   label      = 'Root'          ,
                                                   issue_type = 'root'          )

        candidate = self.create_candidate_from_path(str(self.current_root))

        if candidate is None:
            return Schema__Root__Current__Response(success    = True                     ,
                                                   path       = ''                       ,
                                                   label      = 'Root'                   ,
                                                   issue_type = 'root'                   ,
                                                   message    = 'Previous root invalid, reset to default')

        return Schema__Root__Current__Response(success    = True                  ,
                                               path       = str(candidate.path)   ,
                                               label      = str(candidate.label)  ,
                                               issue_type = str(candidate.issue_type))

    @type_safe
    def set_current_root(self                          ,                         # Set the current root
                         request : Schema__Root__Select__Request
                    ) -> Schema__Root__Select__Response:
        previous_root = self.current_root
        new_path      = request.path

        if self.is_valid_root(new_path) is False:
            return Schema__Root__Select__Response(success  = False                          ,
                                                  path     = ''                             ,
                                                  previous = previous_root                  ,
                                                  message  = f'Invalid root path: {new_path}')

        self.current_root = new_path

        return Schema__Root__Select__Response(success  = True          ,
                                              path     = new_path      ,
                                              previous = previous_root )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Root Validation - Phase 2 (B13): issue.json only
    # ═══════════════════════════════════════════════════════════════════════════════

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

    # ═══════════════════════════════════════════════════════════════════════════════
    # Candidate Creation Helpers
    # ═══════════════════════════════════════════════════════════════════════════════

    def create_issues_root_candidate(self) -> Schema__Root__Candidate:           # Create candidate for .issues/ root
        base_path  = str(self.path_handler.base_path)
        root_path  = self.path_handler.path_for_root_issue()
        root_issue = self.load_issue_from_path(root_path)

        effective_base = base_path if base_path and base_path != '.' else ''
        has_issues     = self.has_issues_folder(effective_base)
        child_count    = self.count_top_level_issues()

        if root_issue:
            return Schema__Root__Candidate(path         = ''                                          ,
                                           label        = root_issue.get('label', 'Root')             ,
                                           title        = root_issue.get('title', 'Issues Root')      ,
                                           issue_type   = root_issue.get('node_type', 'git-repo')     ,
                                           depth        = Safe_UInt(0)                                ,
                                           has_issues   = has_issues                                  ,
                                           has_children = Safe_UInt(child_count)                      )

        return Schema__Root__Candidate(path         = ''              ,
                                       label        = 'Root'          ,
                                       title        = 'Issues Root'   ,
                                       issue_type   = 'root'          ,
                                       depth        = Safe_UInt(0)    ,
                                       has_issues   = has_issues      ,
                                       has_children = Safe_UInt(child_count))

    def create_candidate_from_folder(self, folder_path: str) -> Schema__Root__Candidate:
        issue_data = self.load_issue_summary(folder_path)
        if issue_data is None:
            return None

        base_path     = str(self.path_handler.base_path)
        relative_path = folder_path

        if base_path and base_path != '.':
            prefix = f"{base_path}/"
            if folder_path.startswith(prefix):
                relative_path = folder_path[len(prefix):]

        depth        = self.calculate_depth(folder_path)
        has_issues   = self.has_issues_folder(folder_path)
        child_count  = self.count_children_in_folder(folder_path)

        return Schema__Root__Candidate(path         = relative_path                           ,
                                       label        = issue_data.get('label', '')             ,
                                       title        = issue_data.get('title', '')             ,
                                       issue_type   = issue_data.get('node_type', '')         ,
                                       depth        = Safe_UInt(depth)                        ,
                                       has_issues   = has_issues                              ,
                                       has_children = Safe_UInt(child_count)                  )

    def create_candidate_from_path(self, path: str) -> Schema__Root__Candidate:
        if not path:
            return self.create_issues_root_candidate()

        base_path = str(self.path_handler.base_path)
        full_path = path

        if base_path and base_path != '.':
            if path.startswith(base_path) is False:
                full_path = f"{base_path}/{path}"

        return self.create_candidate_from_folder(full_path)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Folder Scanning - Phase 2 (B13): issue.json only
    # ═══════════════════════════════════════════════════════════════════════════════

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

    def has_issues_folder(self, folder_path: str) -> bool:                       # Check if folder has issues/ subfolder
        issues_folder = f"{folder_path}/issues"
        all_paths     = self.repository.storage_fs.files__paths()
        prefix        = f"{issues_folder}/"

        for path in all_paths:
            if path.startswith(prefix):
                return True

        return False

    def count_top_level_issues(self) -> int:                                     # Count issues in data/ folders
        base_path = str(self.path_handler.base_path)
        data_path = f"{base_path}/data/" if base_path and base_path != '.' else "data/"
        all_paths = self.repository.storage_fs.files__paths()
        folders   = set()

        for path in all_paths:
            if path.startswith(data_path) is False:
                continue
            if path.endswith(f'/{FILE_NAME__ISSUE_JSON}'):                       # Phase 2: issue.json only
                folder = path.rsplit('/', 1)[0]
                folders.add(folder)

        return len(folders)

    def count_children_in_folder(self, folder_path: str) -> int:                 # Count children in issues/ subfolder
        issues_folder = f"{folder_path}/issues/"
        all_paths     = self.repository.storage_fs.files__paths()
        folders       = set()

        for path in all_paths:
            if path.startswith(issues_folder) is False:
                continue
            if path.endswith(f'/{FILE_NAME__ISSUE_JSON}'):                       # Phase 2: issue.json only
                folder = path.rsplit('/', 1)[0]
                folders.add(folder)

        return len(folders)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Issue Data Loading - Phase 2 (B13): issue.json only
    # ═══════════════════════════════════════════════════════════════════════════════

    def load_issue_summary(self, folder_path: str) -> dict:                      # Load issue summary from folder
        issue_path = f"{folder_path}/{FILE_NAME__ISSUE_JSON}"
        return self.load_issue_from_path(issue_path)                             # Phase 2: issue.json only

    def load_issue_from_path(self, file_path: str) -> dict:                      # Load issue data from specific path
        if self.repository.storage_fs.file__exists(file_path) is False:
            return None

        content = self.repository.storage_fs.file__str(file_path)
        if not content:
            return None

        return json_loads(content)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Depth Calculation
    # ═══════════════════════════════════════════════════════════════════════════════

    def calculate_depth(self, folder_path: str) -> int:                          # Calculate nesting depth from root
        base_path = str(self.path_handler.base_path)

        if not folder_path:
            return 0

        if base_path and base_path != '.':
            if folder_path == base_path:
                return 0

            if folder_path.startswith(base_path) is False:
                relative = folder_path
            else:
                relative = folder_path[len(base_path):].strip('/')
        else:
            relative = folder_path.strip('/')

        if not relative:
            return 0

        parts = relative.split('/')

        depth = 0
        for part in parts:
            if part == 'issues':
                depth += 1

        return depth
