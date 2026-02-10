# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Link__Type__Update - Update payload for modifying a link type
# Phase 2 (B16): Supports partial updates to link type definitions
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                             import List
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                            import Safe_Str__Text
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                      import Safe_Str__Link_Verb, Safe_Str__Node_Type


class Schema__Link__Type__Update(Type_Safe):                                     # Link type update payload
    inverse_verb : Safe_Str__Link_Verb         = None                            # Updated inverse verb
    description  : Safe_Str__Text              = None                            # Updated description
    source_types : List[Safe_Str__Node_Type]   = None                            # Updated source types
    target_types : List[Safe_Str__Node_Type]   = None                            # Updated target types
