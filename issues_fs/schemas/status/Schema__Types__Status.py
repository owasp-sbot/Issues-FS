# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Types__Status - Node and link type configuration status
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import List
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                             import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text     import Safe_Str__Text
from mgraph_ai_ui_html_transformation_workbench.schemas.safe_str.Safe_Str__Hex_Color import Safe_Str__Hex_Color


class Schema__Node__Type__Summary(Type_Safe):                                    # Node type summary
    name          : Safe_Str__Text      = ''                                     # Type name (bug, task, etc.)
    display_name  : Safe_Str__Text      = ''                                     # Display name
    color         : Safe_Str__Hex_Color      = ''                                     # Hex color
    status_count  : Safe_UInt           = Safe_UInt(0)                           # Number of statuses defined


class Schema__Link__Type__Summary(Type_Safe):                                    # Link type summary
    verb          : Safe_Str__Text      = ''                                     # Verb (blocks, has-task)
    inverse_verb  : Safe_Str__Text      = ''                                     # Inverse verb
    is_symmetric  : bool                = False                                  # verb == inverse_verb


class Schema__Types__Status(Type_Safe):                      # Type configuration status
    is_initialized    : bool                                 # Types loaded
    node_type_count   : Safe_UInt                            # Number of node types
    link_type_count   : Safe_UInt                            # Number of link types
    node_types        : List[Schema__Node__Type__Summary]    # Node type summaries
    link_types        : List[Schema__Link__Type__Summary]    # Link type summaries
