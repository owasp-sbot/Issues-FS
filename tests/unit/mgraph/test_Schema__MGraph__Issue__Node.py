# ═══════════════════════════════════════════════════════════════════════════════
# test_Schema__MGraph__Issue__Node - Tests for issue node schema (B18)
# Validates Schema__MGraph__Issue__Node pure data container
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                   import Node_Id
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                        import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                   import Safe_Str__File__Path
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                  import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status
from issues_fs.mgraph.Schema__MGraph__Issue__Node                                                   import Schema__MGraph__Issue__Node


class test_Schema__MGraph__Issue__Node(TestCase):

    def test__init__(self):                                                      # Test auto-initialization
        with Schema__MGraph__Issue__Node() as _:
            assert type(_)           is Schema__MGraph__Issue__Node
            assert type(_.node_id)   is Node_Id
            assert type(_.title)     is Safe_Str__Text
            assert type(_.file_path) is Safe_Str__File__Path

    def test__init__with_values(self):                                           # Test initialization with explicit values
        node_id   = Node_Id()
        node      = Schema__MGraph__Issue__Node(node_id   = node_id                                 ,
                                                 label     = Safe_Str__Node_Label('Bug-1')           ,
                                                 title     = Safe_Str__Text('First bug')             ,
                                                 node_type = Safe_Str__Node_Type('bug')              ,
                                                 status    = Safe_Str__Status('todo')                ,
                                                 file_path = Safe_Str__File__Path('data/bug/Bug-1')  )

        assert str(node.label)     == 'Bug-1'
        assert str(node.title)     == 'First bug'
        assert str(node.node_type) == 'bug'
        assert str(node.status)    == 'todo'
        assert str(node.file_path) == 'data/bug/Bug-1'

    def test__inherits_type_safe(self):                                          # Verify Type_Safe inheritance
        assert issubclass(Schema__MGraph__Issue__Node, Type_Safe)

    def test__serialization_round_trip(self):                                    # Test JSON serialization
        node = Schema__MGraph__Issue__Node(node_id   = Node_Id()                                     ,
                                            label     = Safe_Str__Node_Label('Task-1')               ,
                                            title     = Safe_Str__Text('My task')                    ,
                                            node_type = Safe_Str__Node_Type('task')                  ,
                                            status    = Safe_Str__Status('in-progress')              ,
                                            file_path = Safe_Str__File__Path('data/task/Task-1')     )

        json_data = node.json()
        restored  = Schema__MGraph__Issue__Node.from_json(json_data)

        assert str(restored.label)     == 'Task-1'
        assert str(restored.title)     == 'My task'
        assert str(restored.node_type) == 'task'
        assert str(restored.status)    == 'in-progress'
