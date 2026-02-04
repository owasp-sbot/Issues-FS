# ═══════════════════════════════════════════════════════════════════════════════
# test_Graph__Repository__Phase1 - Tests for Phase 1 dual file support
# Tests issue.json preference over node.json for read/write operations
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                       import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                        import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                        import Timestamp_Now
from osbot_utils.utils.Json                                                                             import json_dumps
from issues_fs.schemas.graph.Safe_Str__Graph_Types                     import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status
from issues_fs.schemas.graph.Schema__Node                              import Schema__Node
from issues_fs.issues.graph_services.Graph__Repository         import Graph__Repository
from issues_fs.issues.storage.Path__Handler__Graph_Node        import Path__Handler__Graph_Node


class test_Graph__Repository__Phase_1(TestCase):

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
    # B1: Read Prefers issue.json Over node.json
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__node_load__prefers_issue_json(self):                               # Test issue.json takes priority
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-1')

        path_issue = self.path_handler.path_for_issue_json(node_type, label)     # Create both files with different titles
        path_node  = self.path_handler.path_for_node_json(node_type, label)

        self.write_raw_json_to_path(path_node,  {'title': 'Old Title from node.json' ,
                                                 'node_type': 'bug'                  ,
                                                 'label': 'Bug-1'                    ,
                                                 'status': 'backlog'                 })
        self.write_raw_json_to_path(path_issue, {'title': 'New Title from issue.json',
                                                 'node_type': 'bug'                  ,
                                                 'label': 'Bug-1'                    ,
                                                 'status': 'backlog'                 })

        loaded = self.repository.node_load(node_type, label)

        assert loaded               is not None
        assert str(loaded.title)    == 'New Title from issue.json'               # Should read issue.json

    def test__node_load__falls_back_to_node_json(self):                          # Test fallback when no issue.json
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-2')

        path_node = self.path_handler.path_for_node_json(node_type, label)       # Create only node.json
        self.write_raw_json_to_path(path_node, {'title': 'Legacy node.json',
                                                'node_type': 'bug'         ,
                                                'label': 'Bug-2'           ,
                                                'status': 'backlog'        })

        loaded = self.repository.node_load(node_type, label)

        assert loaded               is not None
        assert str(loaded.title)    == 'Legacy node.json'                        # Should fall back to node.json

    def test__node_load__returns_none_when_neither_exists(self):                 # Test returns None when no file
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-999')

        loaded = self.repository.node_load(node_type, label)

        assert loaded is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # B2: Write Always Creates issue.json
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__node_save__creates_issue_json(self):                               # Test save creates issue.json
        node = self.create_test_node(node_type = 'task'      ,
                                     label     = 'Task-1'    ,
                                     title     = 'New Task'  )

        result = self.repository.node_save(node)

        assert result is True

        path_issue = self.path_handler.path_for_issue_json(node.node_type, node.label)
        path_node  = self.path_handler.path_for_node_json(node.node_type, node.label)

        assert self.repository.storage_fs.file__exists(path_issue) is True       # issue.json should exist
        assert self.repository.storage_fs.file__exists(path_node)  is False      # node.json should NOT be created

    def test__node_save__preserves_existing_node_json(self):                     # Test node.json not deleted on save
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-3')

        path_node = self.path_handler.path_for_node_json(node_type, label)       # Create legacy node.json first
        self.write_raw_json_to_path(path_node, {'title': 'Legacy', 'node_type': 'bug', 'label': 'Bug-3'})

        node = self.create_test_node(node_type = 'bug'     ,                     # Now save via repository
                                     label     = 'Bug-3'   ,
                                     title     = 'Updated' )
        self.repository.node_save(node)

        path_issue = self.path_handler.path_for_issue_json(node_type, label)

        assert self.repository.storage_fs.file__exists(path_issue) is True       # issue.json created
        assert self.repository.storage_fs.file__exists(path_node)  is True       # node.json preserved (Phase 1)

    def test__node_save__round_trip(self):                                       # Test save then load returns same data
        original = self.create_test_node(node_type = 'feature'       ,
                                         label     = 'Feature-1'     ,
                                         title     = 'Test Feature'  )

        self.repository.node_save(original)

        loaded = self.repository.node_load(Safe_Str__Node_Type('feature'),
                                           Safe_Str__Node_Label('Feature-1'))

        assert loaded               is not None
        assert str(loaded.title)    == 'Test Feature'
        assert str(loaded.label)    == 'Feature-1'
        assert str(loaded.node_type)== 'feature'

    # ═══════════════════════════════════════════════════════════════════════════════
    # node_exists Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__node_exists__true_for_issue_json(self):                            # Test exists with issue.json only
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-10')

        path_issue = self.path_handler.path_for_issue_json(node_type, label)
        self.write_raw_json_to_path(path_issue, {'title': 'Test'})

        assert self.repository.node_exists(node_type, label) is True

    def test__node_exists__true_for_node_json(self):                             # Test exists with node.json only
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-11')

        path_node = self.path_handler.path_for_node_json(node_type, label)
        self.write_raw_json_to_path(path_node, {'title': 'Test'})

        assert self.repository.node_exists(node_type, label) is True

    def test__node_exists__false_when_neither(self):                             # Test not exists when no file
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-999')

        assert self.repository.node_exists(node_type, label) is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # node_delete Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__node_delete__removes_both_files(self):                             # Test delete removes both files
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-20')

        path_issue = self.path_handler.path_for_issue_json(node_type, label)     # Create both files
        path_node  = self.path_handler.path_for_node_json(node_type, label)
        self.write_raw_json_to_path(path_issue, {'title': 'Issue'})
        self.write_raw_json_to_path(path_node,  {'title': 'Node'})

        result = self.repository.node_delete(node_type, label)

        assert result                                                   is True
        assert self.repository.storage_fs.file__exists(path_issue)      is False
        assert self.repository.storage_fs.file__exists(path_node)       is False

    def test__node_delete__removes_issue_json_only(self):                        # Test delete when only issue.json
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-21')

        path_issue = self.path_handler.path_for_issue_json(node_type, label)
        self.write_raw_json_to_path(path_issue, {'title': 'Issue'})

        result = self.repository.node_delete(node_type, label)

        assert result                                               is True
        assert self.repository.storage_fs.file__exists(path_issue)  is False

    def test__node_delete__returns_false_when_neither(self):                     # Test delete returns False when nothing
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-999')

        result = self.repository.node_delete(node_type, label)

        assert result is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # nodes_list_labels Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__nodes_list_labels__finds_issue_json(self):                         # Test list finds issue.json files
        node_type = Safe_Str__Node_Type('task')

        path1 = self.path_handler.path_for_issue_json(node_type, Safe_Str__Node_Label('Task-1'))
        path2 = self.path_handler.path_for_issue_json(node_type, Safe_Str__Node_Label('Task-2'))
        self.write_raw_json_to_path(path1, {'title': 'Task 1'})
        self.write_raw_json_to_path(path2, {'title': 'Task 2'})

        labels = self.repository.nodes_list_labels(node_type)

        label_strs = [str(l) for l in labels]
        assert 'Task-1' in label_strs
        assert 'Task-2' in label_strs

    def test__nodes_list_labels__finds_node_json(self):                          # Test list finds node.json files
        node_type = Safe_Str__Node_Type('bug')

        path1 = self.path_handler.path_for_node_json(node_type, Safe_Str__Node_Label('Bug-1'))
        self.write_raw_json_to_path(path1, {'title': 'Bug 1'})

        labels = self.repository.nodes_list_labels(node_type)

        label_strs = [str(l) for l in labels]
        assert 'Bug-1' in label_strs

    def test__nodes_list_labels__no_duplicates(self):                            # Test list doesn't duplicate when both exist
        node_type = Safe_Str__Node_Type('feature')
        label     = Safe_Str__Node_Label('Feature-1')

        path_issue = self.path_handler.path_for_issue_json(node_type, label)     # Create both files for same node
        path_node  = self.path_handler.path_for_node_json(node_type, label)
        self.write_raw_json_to_path(path_issue, {'title': 'Issue'})
        self.write_raw_json_to_path(path_node,  {'title': 'Node'})

        labels = self.repository.nodes_list_labels(node_type)

        label_strs = [str(l) for l in labels]
        assert label_strs.count('Feature-1') == 1                                # Should appear only once

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_issue_file_path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_issue_file_path__returns_issue_json_when_exists(self):         # Test returns issue.json path
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-30')

        path_issue = self.path_handler.path_for_issue_json(node_type, label)
        self.write_raw_json_to_path(path_issue, {'title': 'Test'})

        result = self.repository.get_issue_file_path(node_type, label)

        assert result == path_issue

    def test__get_issue_file_path__returns_node_json_as_fallback(self):          # Test returns node.json as fallback
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-31')

        path_node = self.path_handler.path_for_node_json(node_type, label)
        self.write_raw_json_to_path(path_node, {'title': 'Test'})

        result = self.repository.get_issue_file_path(node_type, label)

        assert result == path_node

    def test__get_issue_file_path__prefers_issue_json(self):                     # Test prefers issue.json over node.json
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-32')

        path_issue = self.path_handler.path_for_issue_json(node_type, label)
        path_node  = self.path_handler.path_for_node_json(node_type, label)
        self.write_raw_json_to_path(path_issue, {'title': 'Issue'})
        self.write_raw_json_to_path(path_node,  {'title': 'Node'})

        result = self.repository.get_issue_file_path(node_type, label)

        assert result == path_issue                                              # Should prefer issue.json

    def test__get_issue_file_path__returns_none_when_neither(self):              # Test returns None when no file
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-999')

        result = self.repository.get_issue_file_path(node_type, label)

        assert result is None
