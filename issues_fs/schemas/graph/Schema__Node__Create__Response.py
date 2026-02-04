# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Create__Response - Response body after creating a node
# POST /api/nodes
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                 import Safe_Str__Text
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node                   import Schema__Node


class Schema__Node__Create__Response(Type_Safe):                                 # Create node response
    success     : bool                  = False                                  # Operation success
    node        : Schema__Node          = None                                   # Created node data
    message     : Safe_Str__Text        = ''                                     # Error message if failed
