# ═══════════════════════════════════════════════════════════════════════════════
# test_Graph__Repository__B12__Delete_Legacy_On_Save - Tests for Phase 2 B12
# Verifies that node_save() deletes legacy node.json after writing issue.json
# and that delete_legacy_node_json works correctly
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                       import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                        import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                        import Timestamp_Now
from osbot_utils.utils.Json                                                                             import json_dumps
from issues_fs.schemas.graph.Safe_Str__Graph_Types               import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status
from issues_fs.schemas.graph.Schema__Node                        import Schema__Node
from issues_fs.issues.graph_services.Graph__Repository   import Graph__Repository
from issues_fs.issues.storage.Path__Handler__Graph_Node  import Path__Handler__Graph_Node


class test_Graph__Repository__B12__Delete_Legacy_On_Save(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup for all tests
        cls.memory_fs    = Memory_FS__In_Memory()
        cls.path_handler = Path__Handler__Graph_Node()
        cls.repository   = Graph__Repository(memory_fs    = cls.memory_fs   ,
                                             path_handler = cls.path_handler)

    def setUp(self):                                                             # Reset storage before each test
        self.repository.clear_storage()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def create_test_node(self                             ,                      # Create a test node
                         node_type : str = 'bug'          ,
                         label     : str = 'Bug-1'        ,
                         title     : str = 'Test Bug'
                    ) -> Schema__Node:
        now = Timestamp_Now()
        return Schema__Node(node_id     = Node_Id(Obj_Id())                     ,
                            node_type   = Safe_Str__Node_Type(node_type),
                            node_index  = Safe_UInt(1)                  ,
                            label       = Safe_Str__Node_Label(label)   ,
                            title       = title                         ,
                            description = ''                            ,
                            status      = Safe_Str__Status('backlog')   ,
                            created_at  = now                           ,
                            updated_at  = now                           ,
                            created_by  = Obj_Id()                      ,
                            tags        = []                            ,
                            links       = []                            ,
                            properties  = {}                            )

    def write_raw_json_to_path(self, path: str, data: dict) -> None:             # Write raw JSON to storage
        content = json_dumps(data, indent=2)
        self.repository.storage_fs.file__save(path, content.encode('utf-8'))

    # ═══════════════════════════════════════════════════════════════════════════════
    # delete_legacy_node_json Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__delete_legacy_node_json__deletes_existing(self):                   # Test deleting existing node.json
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-1')

        path_node = self.path_handler.path_for_node_json(node_type, label)
        self.write_raw_json_to_path(path_node, {'title': 'Legacy'})

        result = self.repository.delete_legacy_node_json(node_type, label)

        assert result                                               is True
        assert self.repository.storage_fs.file__exists(path_node)   is False

    def test__delete_legacy_node_json__returns_false_when_missing(self):          # Test no node.json to delete
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-999')

        result = self.repository.delete_legacy_node_json(node_type, label)

        assert result is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # node_save with B12 Legacy Cleanup Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__node_save__deletes_legacy_node_json(self):                         # Test save removes node.json
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-3')

        path_node = self.path_handler.path_for_node_json(node_type, label)       # Create legacy node.json first
        self.write_raw_json_to_path(path_node, {'title': 'Legacy',
                                                 'node_type': 'bug',
                                                 'label': 'Bug-3'  })

        node = self.create_test_node(node_type = 'bug'     ,                    # Now save via repository
                                     label     = 'Bug-3'   ,
                                     title     = 'Updated' )
        result = self.repository.node_save(node)

        path_issue = self.path_handler.path_for_issue_json(node_type, label)

        assert result                                                is True
        assert self.repository.storage_fs.file__exists(path_issue)   is True    # issue.json created
        assert self.repository.storage_fs.file__exists(path_node)    is False   # node.json deleted (B12)

    def test__node_save__no_error_when_no_legacy(self):                          # Test save works without legacy node.json
        node = self.create_test_node(node_type = 'task'      ,
                                     label     = 'Task-1'    ,
                                     title     = 'New Task'  )

        result = self.repository.node_save(node)

        path_issue = self.path_handler.path_for_issue_json(node.node_type, node.label)
        path_node  = self.path_handler.path_for_node_json(node.node_type, node.label)

        assert result                                                is True
        assert self.repository.storage_fs.file__exists(path_issue)   is True
        assert self.repository.storage_fs.file__exists(path_node)    is False

    def test__node_save__round_trip_after_legacy_cleanup(self):                  # Test save+load after node.json removed
        node_type = Safe_Str__Node_Type('feature')
        label     = Safe_Str__Node_Label('Feature-1')

        path_node = self.path_handler.path_for_node_json(node_type, label)       # Start with legacy
        self.write_raw_json_to_path(path_node, {'title': 'Legacy',
                                                 'node_type': 'feature',
                                                 'label': 'Feature-1'  })

        node = self.create_test_node(node_type = 'feature'        ,
                                     label     = 'Feature-1'      ,
                                     title     = 'Updated Feature')
        self.repository.node_save(node)

        loaded = self.repository.node_load(node_type, label)                     # Load should use issue.json

        assert loaded              is not None
        assert str(loaded.title)   == 'Updated Feature'
        assert str(loaded.label)   == 'Feature-1'
