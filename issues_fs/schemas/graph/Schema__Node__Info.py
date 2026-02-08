# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Info - Node discovery result (Phase 2)
# Pure data container for recursive node discovery
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                       import Safe_Str__File__Path
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                      import Safe_Str__Node_Type, Safe_Str__Node_Label


class Schema__Node__Info(Type_Safe):                                              # Node discovery info
    label     : Safe_Str__Node_Label                                              # e.g., "Task-6"
    path      : Safe_Str__File__Path                                              # e.g., "data/project/Project-1/issues/..."
    node_type : Safe_Str__Node_Type                                               # e.g., "task"
