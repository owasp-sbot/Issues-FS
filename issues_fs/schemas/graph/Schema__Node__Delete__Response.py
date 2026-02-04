# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Delete__Response - Response body after deleting a node
# DELETE /api/nodes/{label}
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                 import Safe_Str__Text
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types          import Safe_Str__Node_Label


class Schema__Node__Delete__Response(Type_Safe):                                 # Delete node response
    success     : bool                  = False                                  # Operation success
    deleted     : bool                  = False                                  # Whether node was deleted
    label       : Safe_Str__Node_Label  = ''                                     # Deleted node label
    message     : Safe_Str__Text        = ''                                     # Error message if failed
