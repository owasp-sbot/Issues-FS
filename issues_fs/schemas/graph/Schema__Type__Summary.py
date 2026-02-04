# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Type__Summary - Summary of node count for a single type
# Used within Schema__Global__Index
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                         import Safe_UInt
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types          import Safe_Str__Node_Type


class Schema__Type__Summary(Type_Safe):                                          # Summary for a node type
    node_type     : Safe_Str__Node_Type                                          # Type name
    count         : Safe_UInt            = Safe_UInt(0)                          # Node count
