# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Link__Create__Response - Response body after creating a link
# Contains both the forward and inverse links created
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                 import Safe_Str__Text
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Link             import Schema__Node__Link


class Schema__Link__Create__Response(Type_Safe):                                 # Create link response
    success      : bool                   = False                                # Operation success
    source_link  : Schema__Node__Link     = None                                 # Link added to source node
    target_link  : Schema__Node__Link     = None                                 # Inverse link added to target
    message      : Safe_Str__Text         = ''                                   # Error message if failed
