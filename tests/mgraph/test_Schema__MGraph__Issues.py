# ═══════════════════════════════════════════════════════════════════════════════
# test_Schema__MGraph__Issues - Tests for MGraph schema layer (B18)
# Validates Schema__MGraph__Issue__Node, Schema__MGraph__Issue__Edge,
# and Schema__MGraph__Issues__Data pure data containers
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                   import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                                   import Edge_Id
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                        import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                   import Safe_Str__File__Path
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                  import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status
from issues_fs.mgraph.Schema__MGraph__Issues                                                        import Schema__MGraph__Issue__Node, Schema__MGraph__Issue__Edge, Schema__MGraph__Issues__Data


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


class test_Schema__MGraph__Issue__Edge(TestCase):

    def test__init__(self):                                                      # Test auto-initialization
        with Schema__MGraph__Issue__Edge() as _:
            assert type(_)          is Schema__MGraph__Issue__Edge
            assert type(_.edge_id)  is Edge_Id
            assert type(_.edge_type) is Safe_Str__Text

    def test__init__with_values(self):                                           # Test with explicit values
        source_id = Node_Id()
        target_id = Node_Id()
        edge      = Schema__MGraph__Issue__Edge(edge_id   = Edge_Id()                       ,
                                                 source_id = source_id                       ,
                                                 target_id = target_id                       ,
                                                 edge_type = Safe_Str__Text('contains')      )

        assert str(edge.edge_type)  == 'contains'
        assert str(edge.source_id)  == str(source_id)
        assert str(edge.target_id)  == str(target_id)

    def test__inherits_type_safe(self):                                          # Verify Type_Safe inheritance
        assert issubclass(Schema__MGraph__Issue__Edge, Type_Safe)

    def test__serialization_round_trip(self):                                    # Test JSON serialization
        edge = Schema__MGraph__Issue__Edge(edge_id   = Edge_Id()                        ,
                                            source_id = Node_Id()                        ,
                                            target_id = Node_Id()                        ,
                                            edge_type = Safe_Str__Text('relates-to')     )

        json_data = edge.json()
        restored  = Schema__MGraph__Issue__Edge.from_json(json_data)

        assert str(restored.edge_type) == 'relates-to'


class test_Schema__MGraph__Issues__Data(TestCase):

    def test__init__(self):                                                      # Test auto-initialization
        with Schema__MGraph__Issues__Data() as _:
            assert type(_)       is Schema__MGraph__Issues__Data
            assert type(_.nodes) is dict
            assert type(_.edges) is dict
            assert len(_.nodes)  == 0
            assert len(_.edges)  == 0

    def test__inherits_type_safe(self):                                          # Verify Type_Safe inheritance
        assert issubclass(Schema__MGraph__Issues__Data, Type_Safe)

    def test__nodes_default_empty_dict(self):                                    # Verify nodes defaults to empty dict
        data = Schema__MGraph__Issues__Data()
        assert data.nodes == {}

    def test__edges_default_empty_dict(self):                                    # Verify edges defaults to empty dict
        data = Schema__MGraph__Issues__Data()
        assert data.edges == {}

    def test__can_store_node(self):                                              # Test storing a node
        data = Schema__MGraph__Issues__Data()
        node = Schema__MGraph__Issue__Node(node_id   = Node_Id()                            ,
                                            label     = Safe_Str__Node_Label('Bug-1')        ,
                                            title     = Safe_Str__Text('A bug')              ,
                                            node_type = Safe_Str__Node_Type('bug')           ,
                                            status    = Safe_Str__Status('todo')             ,
                                            file_path = Safe_Str__File__Path('data/bug/Bug-1'))

        data.nodes[str(node.node_id)] = node

        assert len(data.nodes)                        == 1
        assert str(data.nodes[str(node.node_id)].label) == 'Bug-1'

    def test__can_store_edge(self):                                              # Test storing an edge
        data = Schema__MGraph__Issues__Data()
        edge = Schema__MGraph__Issue__Edge(edge_id   = Edge_Id()                    ,
                                            source_id = Node_Id()                    ,
                                            target_id = Node_Id()                    ,
                                            edge_type = Safe_Str__Text('contains')   )

        data.edges[str(edge.edge_id)] = edge

        assert len(data.edges)                            == 1
        assert str(data.edges[str(edge.edge_id)].edge_type) == 'contains'
