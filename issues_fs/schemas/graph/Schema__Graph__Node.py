from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                        import Safe_Str__Text
from issues_fs.schemas.graph.Safe_Str__Graph_Types                 import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status


class Schema__Graph__Node(Type_Safe):                                            # Node summary for graph response
    label     : Safe_Str__Node_Label
    title     : Safe_Str__Text
    node_type : Safe_Str__Node_Type
    status    : Safe_Str__Status
