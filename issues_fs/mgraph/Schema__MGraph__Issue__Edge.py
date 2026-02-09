# ═══════════════════════════════════════════════════════════════════════════════
# Schema__MGraph__Issue__Edge - Pure data schema for issue edge
# Phase 2 (B18): Four-layer architecture - Schema Layer
#
# CRITICAL: Schema classes contain ONLY type annotations - NO methods
# Business logic belongs in MGraph__Issues__Domain
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                   import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                                   import Edge_Id
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                        import Safe_Str__Text

class Schema__MGraph__Issue__Edge(Type_Safe):                                    # Issue edge data
    edge_id   : Edge_Id                                                          # Unique identifier
    source_id : Node_Id                                                          # Source node ID
    target_id : Node_Id                                                          # Target node ID
    edge_type : Safe_Str__Text                                                   # 'contains', 'relates-to', etc.
