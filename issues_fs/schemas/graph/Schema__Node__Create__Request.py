# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Create__Request - Request body for creating a new node
# POST /api/nodes
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                         import List, Dict, Any
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                        import Safe_Str__Text
from issues_fs.schemas.graph.Safe_Str__Graph_Types                 import Safe_Str__Node_Type, Safe_Str__Status
from issues_fs.schemas.safe_str.Safe_Str__Issue__Node__Description import Safe_Str__Issue__Node__Description


class Schema__Node__Create__Request(Type_Safe):                                  # Create node request
    node_type   : Safe_Str__Node_Type                                            # Required: "bug", "task", etc.
    title       : Safe_Str__Text                                                 # Required: display title
    description : Safe_Str__Issue__Node__Description                             # Optional description
    status      : Safe_Str__Status      = None                                   # Optional: defaults to type's default
    tags        : List[Safe_Str__Text]                                           # Optional tags
    properties  : Dict[str, Any]                                                 # Type-specific properties
