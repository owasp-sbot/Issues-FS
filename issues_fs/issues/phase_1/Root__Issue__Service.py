# ═══════════════════════════════════════════════════════════════════════════════
# Root__Issue__Service - Service for creating and managing the root issue
# Phase 1: Creates GitRepo-1 issue in .issues/issue.json
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                            import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                       import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                        import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                        import Timestamp_Now
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
from osbot_utils.utils.Json                                                                             import json_dumps, json_loads
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types                     import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node                              import Schema__Node
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository         import Graph__Repository
from mgraph_ai_ui_html_transformation_workbench.service.issues.storage.Path__Handler__Graph_Node        import Path__Handler__Graph_Node


# ═══════════════════════════════════════════════════════════════════════════════
# Constants for Root Issue
# ═══════════════════════════════════════════════════════════════════════════════

ROOT_ISSUE_TYPE         = 'git-repo'
ROOT_ISSUE_LABEL        = 'Gitrepo-1'
ROOT_ISSUE_DEFAULT_TITLE = 'Project Issues'
ROOT_ISSUE_STATUS       = 'active'


class Root__Issue__Service(Type_Safe):                                           # Service for root issue management
    repository   : Graph__Repository                                             # Data access layer
    path_handler : Path__Handler__Graph_Node                                     # Path generation

    # ═══════════════════════════════════════════════════════════════════════════════
    # Root Issue Initialization
    # ═══════════════════════════════════════════════════════════════════════════════

    def ensure_root_issue_exists(self                                   ,        # Create root issue if not exists
                                 title : str = ROOT_ISSUE_DEFAULT_TITLE
                            ) -> bool:
        if self.root_issue_exists():
            return True                                                          # Already exists

        return self.create_root_issue(title=title)

    @type_safe
    def create_root_issue(self                                   ,               # Create the root GitRepo-1 issue
                          title : str = ROOT_ISSUE_DEFAULT_TITLE
                     ) -> bool:
        if self.root_issue_exists():                                             # Don't overwrite existing
            return False

        now = Timestamp_Now()

        root_issue = Schema__Node(node_id     = Node_Id(Obj_Id())                                 ,
                                  node_type   = Safe_Str__Node_Type(ROOT_ISSUE_TYPE)      ,
                                  node_index  = Safe_UInt(1)                              ,
                                  label       = Safe_Str__Node_Label(ROOT_ISSUE_LABEL)    ,
                                  title       = title                                     ,
                                  description = 'Root issue for all project issues'       ,
                                  status      = Safe_Str__Status(ROOT_ISSUE_STATUS)       ,
                                  created_at  = now                                       ,
                                  updated_at  = now                                       ,
                                  created_by  = Obj_Id()                                  ,
                                  tags        = []                                        ,
                                  links       = []                                        ,
                                  properties  = {}                                        )

        return self.save_root_issue(root_issue)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Root Issue Persistence
    # ═══════════════════════════════════════════════════════════════════════════════

    def save_root_issue(self, root_issue: Schema__Node) -> bool:                 # Save root issue to .issues/issue.json
        path    = self.path_handler.path_for_root_issue()
        data    = root_issue.json()
        content = json_dumps(data, indent=2)
        return self.repository.storage_fs.file__save(path, content.encode('utf-8'))

    def root_issue_exists(self) -> bool:                                         # Check if root issue.json exists
        path = self.path_handler.path_for_root_issue()
        return self.repository.storage_fs.file__exists(path)

    def load_root_issue(self) -> Schema__Node:                                   # Load the root issue
        path = self.path_handler.path_for_root_issue()

        if self.repository.storage_fs.file__exists(path) is False:
            return None

        content = self.repository.storage_fs.file__str(path)
        if not content:
            return None

        data = json_loads(content)
        if data is None:
            return None

        return Schema__Node.from_json(data)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Root Issue Updates
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def update_root_issue_title(self, title: Safe_Str__Text) -> bool:            # Update root issue title
        root_issue = self.load_root_issue()
        if root_issue is None:
            return False

        root_issue.title      = str(title)
        root_issue.updated_at = Timestamp_Now()

        return self.save_root_issue(root_issue)

    @type_safe
    def update_root_issue_description(self                          ,            # Update root issue description
                                      description : Safe_Str__Text
                                 ) -> bool:
        root_issue = self.load_root_issue()
        if root_issue is None:
            return False

        root_issue.description = str(description)
        root_issue.updated_at  = Timestamp_Now()

        return self.save_root_issue(root_issue)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Root Issue Deletion (for testing)
    # ═══════════════════════════════════════════════════════════════════════════════

    def delete_root_issue(self) -> bool:                                         # Delete root issue (for tests)
        path = self.path_handler.path_for_root_issue()
        if self.repository.storage_fs.file__exists(path):
            return self.repository.storage_fs.file__delete(path)
        return False