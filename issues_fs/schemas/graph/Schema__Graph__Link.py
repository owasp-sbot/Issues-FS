from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types import Safe_Str__Node_Label, Safe_Str__Link_Verb

# todo, see if we shouldn't call 'link_type' 'link_verb'
class Schema__Graph__Link(Type_Safe):                                            # Link for graph response
    source    : Safe_Str__Node_Label
    target    : Safe_Str__Node_Label
    link_type : Safe_Str__Link_Verb                                              # verb like "has-task", "blocks"