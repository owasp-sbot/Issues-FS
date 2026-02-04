# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Link__List__Response - Response body for listing links from a node
# GET /api/nodes/{label}/links
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                  import List
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                 import Safe_Str__Text
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Link             import Schema__Node__Link


class Schema__Link__List__Response(Type_Safe):                                   # List links response
    success      : bool                      = False                             # Operation success
    links        : List[Schema__Node__Link]                                      # Links from node
    message      : Safe_Str__Text            = ''                                # Error message if failed
