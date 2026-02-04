# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Global__Index - Global index for entire graph
# Stored at .issues/_index.json - tracks total nodes and per-type counts
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                  import List
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                         import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now             import Timestamp_Now
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Type__Summary          import Schema__Type__Summary


class Schema__Global__Index(Type_Safe):                                          # Global index file (.issues/_index.json)
    total_nodes   : Safe_UInt            = Safe_UInt(0)                          # Total nodes across all types
    last_updated  : Timestamp_Now        = None                                  # ISO timestamp of last update
    type_counts   : List[Schema__Type__Summary]                                  # Count per type
