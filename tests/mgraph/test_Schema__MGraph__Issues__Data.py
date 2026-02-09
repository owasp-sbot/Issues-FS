# ═══════════════════════════════════════════════════════════════════════════════
# test_Schema__MGraph__Issues__Data - Tests for graph data container schema (B18)
# Validates Schema__MGraph__Issues__Data pure data container
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict                               import Type_Safe__Dict
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                   import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                                   import Edge_Id
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                        import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                   import Safe_Str__File__Path
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                  import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status
from issues_fs.mgraph.Schema__MGraph__Issue__Node                                                   import Schema__MGraph__Issue__Node
from issues_fs.mgraph.Schema__MGraph__Issue__Edge                                                   import Schema__MGraph__Issue__Edge
from issues_fs.mgraph.Schema__MGraph__Issues__Data                                                  import Schema__MGraph__Issues__Data


class test_Schema__MGraph__Issues__Data(TestCase):

    def test__init__(self):                                                      # Test auto-initialization
        with Schema__MGraph__Issues__Data() as _:
            assert type(_)       is Schema__MGraph__Issues__Data
            assert type(_.nodes) is Type_Safe__Dict
            assert type(_.edges) is Type_Safe__Dict
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
