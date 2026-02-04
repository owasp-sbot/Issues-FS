# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Link__Create__Request - Request body for creating a link between nodes
# POST /api/nodes/{label}/links
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types          import Safe_Str__Link_Verb, Safe_Str__Node_Label


class Schema__Link__Create__Request(Type_Safe):                                  # Create link request
    verb         : Safe_Str__Link_Verb                                           # Required: "blocks", "has-task"
    target_label : Safe_Str__Node_Label                                          # Required: target node label
