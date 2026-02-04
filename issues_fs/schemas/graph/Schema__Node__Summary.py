# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Summary - Lightweight node summary for list responses
# Contains only essential fields for display in lists
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                import Safe_Str__Text
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types         import Safe_Str__Node_Label, Safe_Str__Node_Type, Safe_Str__Status


class Schema__Node__Summary(Type_Safe):                                          # Node summary for listings
    label       : Safe_Str__Node_Label                                           # "Bug-27"
    node_type   : Safe_Str__Node_Type                                            # "bug"
    title       : Safe_Str__Text                                                 # Display title
    status      : Safe_Str__Status                                               # Current status