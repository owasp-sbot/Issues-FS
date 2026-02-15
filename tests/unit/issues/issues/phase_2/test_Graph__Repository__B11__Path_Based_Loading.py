# ═══════════════════════════════════════════════════════════════════════════════
# test_Graph__Repository__B11__Path_Based_Loading - Tests for Phase 2 B11
# Path-based node loading: node_load_by_path, node_find_path_by_label,
# node_load_by_label, and Node__Service.get_node_by_path
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                       import Safe_Str__File__Path
from osbot_utils.utils.Json                                                                             import json_dumps
from issues_fs.schemas.graph.Safe_Str__Graph_Types               import Safe_Str__Node_Type, Safe_Str__Node_Label
from issues_fs.schemas.graph.Schema__Node                        import Schema__Node
from issues_fs.schemas.graph.Schema__Node__Response              import Schema__Node__Response
from issues_fs.issues.graph_services.Graph__Repository   import Graph__Repository
from issues_fs.issues.graph_services.Node__Service       import Node__Service
from issues_fs.issues.storage.Path__Handler__Graph_Node  import Path__Handler__Graph_Node


class test_Graph__Repository__B11__Path_Based_Loading(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup for all tests
        cls.memory_fs    = Memory_FS__In_Memory()
        cls.path_handler = Path__Handler__Graph_Node()
        cls.repository   = Graph__Repository(memory_fs    = cls.memory_fs   ,
                                             path_handler = cls.path_handler)
        cls.node_service = Node__Service(repository = cls.repository)

    def setUp(self):                                                             # Reset storage before each test
        self.repository.clear_storage()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def write_raw_json_to_path(self, path: str, data: dict) -> None:             # Write raw JSON to storage
        content = json_dumps(data, indent=2)
        self.repository.storage_fs.file__save(path, content.encode('utf-8'))

    # ═══════════════════════════════════════════════════════════════════════════════
    # node_load_by_path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__node_load_by_path__loads_from_folder(self):                        # Test loading by explicit path
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json',
                                     {'node_type': 'bug'    ,
                                      'label'    : 'Bug-1'  ,
                                      'title'    : 'Test Bug',
                                      'status'   : 'backlog'})

        node = self.repository.node_load_by_path(
            Safe_Str__File__Path('.issues/data/bug/Bug-1'))

        assert node              is not None
        assert str(node.label)   == 'Bug-1'
        assert str(node.title)   == 'Test Bug'

    def test__node_load_by_path__nested_issue(self):                             # Test loading nested issue by path
        self.write_raw_json_to_path(
            '.issues/data/project/Project-1/issues/Task-1/issue.json',
            {'node_type': 'task'       ,
             'label'    : 'Task-1'     ,
             'title'    : 'Nested Task',
             'status'   : 'backlog'    })

        node = self.repository.node_load_by_path(
            Safe_Str__File__Path('.issues/data/project/Project-1/issues/Task-1'))

        assert node            is not None
        assert str(node.label) == 'Task-1'
        assert str(node.title) == 'Nested Task'

    def test__node_load_by_path__returns_none_when_missing(self):                # Test missing path
        node = self.repository.node_load_by_path(
            Safe_Str__File__Path('.issues/data/bug/Bug-999'))

        assert node is None

    def test__node_load_by_path__ignores_node_json(self):                        # Test that node.json is not loaded
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/node.json',
                                     {'node_type': 'bug', 'label': 'Bug-1'})

        node = self.repository.node_load_by_path(
            Safe_Str__File__Path('.issues/data/bug/Bug-1'))

        assert node is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # node_find_path_by_label Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__node_find_path_by_label__finds_top_level(self):                    # Test finding top-level label
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json',
                                     {'node_type': 'bug', 'label': 'Bug-1'})

        path = self.repository.node_find_path_by_label(
            Safe_Str__Node_Label('Bug-1'))

        assert path is not None
        assert str(path) == '.issues/data/bug/Bug-1'

    def test__node_find_path_by_label__finds_nested(self):                       # Test finding nested label
        self.write_raw_json_to_path(
            '.issues/data/project/Project-1/issues/Task-1/issue.json',
            {'node_type': 'task', 'label': 'Task-1'})

        path = self.repository.node_find_path_by_label(
            Safe_Str__Node_Label('Task-1'))

        assert path is not None
        assert str(path) == '.issues/data/project/Project-1/issues/Task-1'

    def test__node_find_path_by_label__returns_none_for_missing(self):           # Test missing label
        path = self.repository.node_find_path_by_label(
            Safe_Str__Node_Label('Bug-999'))

        assert path is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # node_load_by_label Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__node_load_by_label__loads_by_label(self):                          # Test loading by label search
        self.write_raw_json_to_path('.issues/data/task/Task-1/issue.json',
                                     {'node_type': 'task'        ,
                                      'label'    : 'Task-1'      ,
                                      'title'    : 'Found by label',
                                      'status'   : 'backlog'     })

        node = self.repository.node_load_by_label(
            Safe_Str__Node_Label('Task-1'))

        assert node            is not None
        assert str(node.title) == 'Found by label'

    def test__node_load_by_label__returns_none_for_missing(self):                # Test missing label
        node = self.repository.node_load_by_label(
            Safe_Str__Node_Label('Task-999'))

        assert node is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node__Service.get_node_by_path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__service_get_node_by_path__success(self):                           # Test service returns response on success
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json',
                                     {'node_type': 'bug'     ,
                                      'label'    : 'Bug-1'   ,
                                      'title'    : 'Test Bug',
                                      'status'   : 'backlog' })

        response = self.node_service.get_node_by_path(
            Safe_Str__File__Path('.issues/data/bug/Bug-1'))

        assert type(response) is Schema__Node__Response
        assert response.success              is True
        assert response.node                 is not None
        assert str(response.node.label)      == 'Bug-1'

    def test__service_get_node_by_path__not_found(self):                         # Test service returns failure on missing
        response = self.node_service.get_node_by_path(
            Safe_Str__File__Path('.issues/data/bug/Bug-999'))

        assert response.success is False
        assert response.node    is None
