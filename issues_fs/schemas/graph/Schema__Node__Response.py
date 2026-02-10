# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Response - Response wrapper for single node operations (Phase 2)
# Pure data container for path-based and hierarchical node loading
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                            import Safe_Str__Text
from issues_fs.schemas.graph.Schema__Node                                                               import Schema__Node


class Schema__Node__Response(Type_Safe):                                          # Node response wrapper
    success : bool             = False                                            # Operation success flag
    node    : Schema__Node     = None                                             # The loaded node (if found)
    message : Safe_Str__Text                                                      # Error/status message
