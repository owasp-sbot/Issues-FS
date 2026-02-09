# ═══════════════════════════════════════════════════════════════════════════════
# Schema__MGraph__Issue__Node - Pure data schema for issue node
# Phase 2 (B18): Four-layer architecture - Schema Layer
#
# CRITICAL: Schema classes contain ONLY type annotations - NO methods
# Business logic belongs in MGraph__Issues__Domain
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                   import Node_Id
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                        import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                   import Safe_Str__File__Path
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                  import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status

class Schema__MGraph__Issue__Node(Type_Safe):                                    # Issue node data
    node_id   : Node_Id                                                          # Unique identifier
    label     : Safe_Str__Node_Label                                             # Display label (e.g., "Task-6")
    title     : Safe_Str__Text                                                   # Human-readable title
    node_type : Safe_Str__Node_Type                                              # Type (e.g., "task")
    status    : Safe_Str__Status                                                 # Current status
    file_path : Safe_Str__File__Path                                             # Filesystem path to issue.json folder
