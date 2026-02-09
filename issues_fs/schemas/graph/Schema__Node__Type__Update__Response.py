# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Type__Update__Response - Response for node type update
# Phase 2 (B15): Returns result of a node type update operation
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                            import Safe_Str__Text


class Schema__Node__Type__Update__Response(Type_Safe):                           # Response for node type update
    success   : bool             = False                                         # Whether update succeeded
    node_type : object           = None                                          # Updated node type (Schema__Node__Type)
    message   : Safe_Str__Text                                                   # Status message
