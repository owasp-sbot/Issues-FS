# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Type__Index - Per-type index tracking for node counts and next ID
# Stored at .issues/data/{node_type}/_index.json
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                        import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now            import Timestamp_Now
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types         import Safe_Str__Node_Type


class Schema__Type__Index(Type_Safe):                                            # Per-type index file
    node_type     : Safe_Str__Node_Type                                          # "bug", "task", etc.
    next_index    : Safe_UInt            = Safe_UInt(1)                          # Next available index
    count         : Safe_UInt            = Safe_UInt(0)                          # Total nodes of this type
    last_updated  : Timestamp_Now        = None                                  # ISO timestamp
