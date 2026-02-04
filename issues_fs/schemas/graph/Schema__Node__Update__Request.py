# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Update__Request - Request body for updating an existing node
# PATCH /api/nodes/{label} - All fields optional (partial update)
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                  import List, Dict, Any
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                 import Safe_Str__Text
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types          import Safe_Str__Status
from mgraph_ai_ui_html_transformation_workbench.schemas.safe_str.Safe_Str__Issue__Node__Description import Safe_Str__Issue__Node__Description


class Schema__Node__Update__Request(Type_Safe):                                  # Update node request (partial)
    title       : Safe_Str__Text                     = None                      # New title
    description : Safe_Str__Issue__Node__Description = None                      # New description
    status      : Safe_Str__Status                   = None                      # New status
    tags        : List[Safe_Str__Text]               = None                      # New tags (replaces existing)
    properties  : Dict[str, Any]                     = None                      # New properties (merged)
