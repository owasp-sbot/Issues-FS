# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node__Link - Relationship edge between nodes
# Links are bidirectional and denormalized (stored on both ends)
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                    import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now    import Timestamp_Now
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types import Safe_Str__Link_Verb, Safe_Str__Node_Label


class Schema__Node__Link(Type_Safe):                                             # Relationship to another node
    link_type_id  : Obj_Id                                                       # Reference to link type definition
    verb          : Safe_Str__Link_Verb                                          # "blocks", "has-task", "assigned-to"
    target_id     : Obj_Id                                                       # Target node's node_id
    target_label  : Safe_Str__Node_Label                                         # Denormalized: "Task-15" for display
    created_at    : Timestamp_Now                                                # When link was created
