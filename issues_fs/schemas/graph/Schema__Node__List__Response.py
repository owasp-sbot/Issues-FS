# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__List__Response - Response body for listing nodes
# GET /api/nodes or GET /api/nodes/type/{node_type}
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                  import List
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                 import Safe_Str__Text
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Summary          import Schema__Node__Summary


class Schema__Node__List__Response(Type_Safe):                                   # List nodes response
    success     : bool                        = False                            # Operation success
    nodes       : List[Schema__Node__Summary]                                    # Node summaries
    total       : int                         = 0                                # Total count
    message     : Safe_Str__Text              = ''                               # Error message if failed