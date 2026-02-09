# ═══════════════════════════════════════════════════════════════════════════════
# test_Schema__MGraph__Issue__Edge - Tests for issue edge schema (B18)
# Validates Schema__MGraph__Issue__Edge pure data container
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                   import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                                   import Edge_Id
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                        import Safe_Str__Text
from issues_fs.mgraph.Schema__MGraph__Issue__Edge                                                   import Schema__MGraph__Issue__Edge


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
