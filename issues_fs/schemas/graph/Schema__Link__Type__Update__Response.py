# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Link__Type__Update__Response - Response for link type update
# Phase 2 (B16): Returns result of a link type update operation
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                            import Safe_Str__Text


class Schema__Link__Type__Update__Response(Type_Safe):                           # Response for link type update
    success   : bool             = False                                         # Whether update succeeded
    link_type : object           = None                                          # Updated link type (Schema__Link__Type)
    message   : Safe_Str__Text                                                   # Status message
