# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Type__Update - Update payload for modifying a node type
# Phase 2 (B15): Supports partial updates to node type definitions
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                             import List
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                            import Safe_Str__Text
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                      import Safe_Str__Node_Type_Display, Safe_Str__Status
from issues_fs.schemas.safe_str.Safe_Str__Hex_Color                                                     import Safe_Str__Hex_Color


class Schema__Node__Type__Update(Type_Safe):                                     # Node type update payload
    display_name   : Safe_Str__Node_Type_Display = None                          # Updated display name
    description    : Safe_Str__Text              = None                          # Updated description
    icon           : Safe_Str__Text              = None                          # Updated icon
    color          : Safe_Str__Hex_Color         = None                          # Updated color
    statuses       : List[Safe_Str__Status]      = None                          # Updated valid statuses
    default_status : Safe_Str__Status            = None                          # Updated default status
