# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Type - Definition of a node type (bug, task, feature, etc.)
# Each type has its own statuses, properties, and display configuration
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                  import List
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                 import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                             import Obj_Id
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types          import Safe_Str__Node_Type, Safe_Str__Node_Type_Display, Safe_Str__Status
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Property__Definition   import Schema__Property__Definition
from mgraph_ai_ui_html_transformation_workbench.schemas.safe_str.Safe_Str__Hex_Color         import Safe_Str__Hex_Color

# todo: refactor to Schema__Issue__Node__Type
#       (do the same *__Issue__* refactoring where applicable
class Schema__Node__Type(Type_Safe):                                             # Node type definition
    #todo: refactor to Issue__Node__Type_Id
    type_id        : Obj_Id                                                      # Unique identifier for this type
    name           : Safe_Str__Node_Type                                         # "bug", "task", "feature"
    display_name   : Safe_Str__Node_Type_Display                                 # "Bug", "Task", "Feature"
    description    : Safe_Str__Text                                              # What this type represents
    icon           : Safe_Str__Text                                              # Icon identifier (optional)
    color          : Safe_Str__Hex_Color                                         # Display color like #ef4444

    statuses       : List[Safe_Str__Status]                                      # Valid statuses for this type
    default_status : Safe_Str__Status                                            # Initial status for new nodes

    properties     : List[Schema__Property__Definition]                          # Type-specific field definitions
