# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Link__Type - Definition of a relationship type (blocks, has-task, etc.)
# Link types define the semantics of relationships between nodes
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                  import List
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                 import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                             import Obj_Id
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types          import Safe_Str__Link_Verb, Safe_Str__Node_Type

# todo: set link_type_id to Issue__Link_Type__Id  (or Issue__Link__Type__Id)
class Schema__Link__Type(Type_Safe):                                             # Link type definition
    link_type_id  : Obj_Id                                                       # Unique identifier
    verb          : Safe_Str__Link_Verb                                          # "blocks", "has-task"
    inverse_verb  : Safe_Str__Link_Verb                                          # "blocked-by", "task-of"
    description   : Safe_Str__Text                                               # What this relationship means

    source_types  : List[Safe_Str__Node_Type]                                    # Valid source node types
    target_types  : List[Safe_Str__Node_Type]                                    # Valid target node types
