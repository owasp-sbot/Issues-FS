# ═══════════════════════════════════════════════════════════════════════════════
# Path__Handler__Graph_Node - Path generation for graph-based issue tracking
# Phase 1: Added dual file support (issue.json preferred, node.json fallback)
#
# Storage structure:
#   data/{node_type}/{Label}/issue.json    <- NEW: Preferred file
#   data/{node_type}/{Label}/node.json     <- LEGACY: Read-only fallback
#   data/{node_type}/{Label}/attachments/{filename}
#   data/{node_type}/_index.json
#   config/node-types.json
#   config/link-types.json
#   _index.json
#   issue.json                             <- NEW: Root issue (optional)
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                               import type_safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path            import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Name            import Safe_Str__File__Name
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                           import Safe_Str__Node_Type, Safe_Str__Node_Label


# ═══════════════════════════════════════════════════════════════════════════════
# File Name Constants
# ═══════════════════════════════════════════════════════════════════════════════

FILE_NAME__ISSUE_JSON = 'issue.json'                                             # NEW: Preferred issue data file
FILE_NAME__NODE_JSON  = 'node.json'                                              # LEGACY: Fallback for backward compat

# todo: quite a number of raw primitives used below (which need to type safe primitives)
#       also this class has tons of path injections
#       we need to do a serious rethink on how this path works ,since even the use of "/data" is wrong below since in the new layout it should be issues

class Path__Handler__Graph_Node(Type_Safe):                                      # Path handler for graph nodes
    base_path : Safe_Str__File__Path = '.issues'                                 # Root directory for issues (empty or '.' for local disk)

    def path_prefix(self) -> str:                                                # Get prefix for paths (empty or base_path/)
        if self.base_path and str(self.base_path) != '.':
            return f"{self.base_path}/"
        return ""

    def has_base_path(self) -> bool:                                             # Check if base_path is set (not empty or '.')
        return bool(self.base_path) and str(self.base_path) != '.'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Issue File Paths (Phase 1: Dual File Support)
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def path_for_issue_json(self                              ,                  # Path to issue.json (preferred)
                            node_type : Safe_Str__Node_Type   ,
                            label     : Safe_Str__Node_Label
                       ) -> Safe_Str__File__Path:
        # note: the code below doesn't really make sense since the base paths should be set by the storage
        # if self.has_base_path():
        #     return f"{self.base_path}/data/{node_type}/{label}/{FILE_NAME__ISSUE_JSON}"
        return f"data/{node_type}/{label}/{FILE_NAME__ISSUE_JSON}"

    @type_safe
    def path_for_node_json(self                              ,                   # Path to node.json (legacy)
                           node_type : Safe_Str__Node_Type   ,
                           label     : Safe_Str__Node_Label
                      ) -> str:
        return f"data/{node_type}/{label}/{FILE_NAME__NODE_JSON}"

    @type_safe
    def path_for_node(self                              ,                        # DEPRECATED: Use path_for_issue_json
                      node_type : Safe_Str__Node_Type   ,                        # Kept for backward compatibility
                      label     : Safe_Str__Node_Label
                 ) -> str:
        return self.path_for_node_json(node_type, label)                         # Returns legacy path

    @type_safe
    def path_for_node_folder(self                              ,                 # Path to node folder
                             node_type : Safe_Str__Node_Type   ,
                             label     : Safe_Str__Node_Label
                        ) -> str:
        return f"data/{node_type}/{label}"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Root Issue Path (Phase 1: Root issue support)
    # ═══════════════════════════════════════════════════════════════════════════════

    def path_for_root_issue(self) -> str:                                        # Path to root issue.json
        return FILE_NAME__ISSUE_JSON

    # ═══════════════════════════════════════════════════════════════════════════════
    # Child Issues Folder (Phase 1: Hierarchical structure)
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def path_for_issues_folder(self                              ,               # Path to issues/ subfolder
                               node_type : Safe_Str__Node_Type   ,
                               label     : Safe_Str__Node_Label
                          ) -> str:
        return f"data/{node_type}/{label}/issues"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Attachment Paths
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def path_for_attachment(self                              ,                  # Path to attachment file
                            node_type : Safe_Str__Node_Type   ,
                            label     : Safe_Str__Node_Label  ,
                            filename  : Safe_Str__File__Name
                       ) -> str:
        return f"data/{node_type}/{label}/attachments/{filename}"

    @type_safe
    def path_for_attachments_folder(self                              ,          # Path to attachments folder
                                    node_type : Safe_Str__Node_Type   ,
                                    label     : Safe_Str__Node_Label
                               ) -> str:
        return f"data/{node_type}/{label}/attachments"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Index Paths
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def path_for_type_index(self                              ,                  # Path to per-type index
                            node_type : Safe_Str__Node_Type
                       ) -> str:
        return f"data/{node_type}/_index.json"

    def path_for_global_index(self) -> str:                                      # Path to global index
        return "_index.json"

    @type_safe
    def path_for_type_folder(self                              ,                 # Path to type folder
                             node_type : Safe_Str__Node_Type
                        ) -> str:
        return f"data/{node_type}"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Config Paths
    # ═══════════════════════════════════════════════════════════════════════════════

    def path_for_node_types(self) -> str:                                        # Path to node-types.json
        return "config/node-types.json"

    def path_for_link_types(self) -> str:                                        # Path to link-types.json
        return "config/link-types.json"

    def path_for_settings(self) -> str:                                          # Path to settings.json
        return "config/settings.json"

    def path_for_config_folder(self) -> str:                                     # Path to config folder
        return "config"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Label Generation
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def label_from_type_and_index(self                              ,            # Generate label from type + index
                                  node_type  : Safe_Str__Node_Type  ,            # e.g., "bug"
                                  node_index : int                               # e.g., 27
                             ) -> Safe_Str__Node_Label:
        display_type = node_type.capitalize()                                    # "bug" → "Bug"
        return Safe_Str__Node_Label(f"{display_type}-{node_index}")              # "Bug-27"