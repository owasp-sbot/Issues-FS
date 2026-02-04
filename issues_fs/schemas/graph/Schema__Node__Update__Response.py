# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Update__Response - Response body after updating a node
# PATCH /api/nodes/{label}
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                 import Safe_Str__Text
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node                   import Schema__Node


class Schema__Node__Update__Response(Type_Safe):                                 # Update node response
    success     : bool                  = False                                  # Operation success
    node        : Schema__Node          = None                                   # Updated node data
    message     : Safe_Str__Text        = ''                                     # Error message if failed
