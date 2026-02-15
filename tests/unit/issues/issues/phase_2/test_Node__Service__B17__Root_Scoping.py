# ═══════════════════════════════════════════════════════════════════════════════
# test_Node__Service__B17__Root_Scoping - Tests for Phase 2 B17
# Verifies that list_nodes() and list_nodes_for_type() respect root scoping
# via root_selection_service, and that get_current_root_path() works correctly
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                       import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                        import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                        import Timestamp_Now
from osbot_utils.utils.Json                                                                             import json_dumps
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                      import Safe_Str__Node_Type, Safe_Str__Node_Label
from issues_fs.schemas.graph.Schema__Node                                                               import Schema__Node
from issues_fs.issues.graph_services.Graph__Repository                                                  import Graph__Repository
from issues_fs.issues.graph_services.Node__Service                                                      import Node__Service
from issues_fs.issues.graph_services.Type__Service                                                      import Type__Service
from issues_fs.issues.storage.Path__Handler__Graph_Node                                                 import Path__Handler__Graph_Node


class Mock__Root__Selection__Service(Type_Safe):                             # Mock root selection service
    current_root : Safe_Str__File__Path                                      # Current root path


class test_Node__Service__B17__Root_Scoping(TestCase):

    @classmethod
    def setUpClass(cls):                                                     # Shared setup for all tests
        cls.memory_fs    = Memory_FS__In_Memory()
        cls.path_handler = Path__Handler__Graph_Node()
        cls.repository   = Graph__Repository(memory_fs    = cls.memory_fs   ,
                                              path_handler = cls.path_handler)
        cls.type_service = Type__Service(repository=cls.repository)

    def setUp(self):                                                         # Reset storage before each test
        self.repository.clear_storage()
        self.type_service.initialize_default_types()                         # Re-initialize after clear
        self.type_service.create_node_type(name         = Safe_Str__Node_Type('project'),  # Register project type for tests
                                            display_name = 'Project'                     ,
                                            description  = 'Project container'           )

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def write_raw_json_to_path(self, path, data):                            # Write raw JSON to storage
        content = json_dumps(data, indent=2)
        self.repository.storage_fs.file__save(path, content.encode("utf-8"))

    def create_issue_at_path(self, path, node_type, label, title="Test"):    # Create a full issue at a path
        now = Timestamp_Now()
        data = { "node_id"    : str(Obj_Id())    ,
                 "node_type"  : node_type         ,
                 "node_index" : 1                 ,
                 "label"      : label             ,
                 "title"      : title             ,
                 "status"     : "backlog"         ,
                 "created_at" : str(now)          ,
                 "updated_at" : str(now)          ,
                 "created_by" : str(Obj_Id())     ,
                 "tags"       : []                ,
                 "links"      : []                ,
                 "properties" : {}                }
        self.write_raw_json_to_path(path, data)

    # ═══════════════════════════════════════════════════════════════════════════
    # get_current_root_path Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__get_current_root_path__no_root_service(self):                  # Returns None when no root service
        service = Node__Service(repository=self.repository)
        result  = service.get_current_root_path()
        assert result is None

    def test__get_current_root_path__empty_root(self):                       # Returns None when root is empty
        mock_root = Mock__Root__Selection__Service()
        service   = Node__Service(repository             = self.repository,
                                   root_selection_service = mock_root      )
        result    = service.get_current_root_path()
        assert result is None

    def test__get_current_root_path__with_root_set(self):                    # Returns root path when set
        mock_root              = Mock__Root__Selection__Service()
        mock_root.current_root = Safe_Str__File__Path(".issues/data/project/Project-1")
        service                = Node__Service(repository             = self.repository,
                                                root_selection_service = mock_root      )
        result = service.get_current_root_path()
        assert result      is not None
        assert str(result)  == ".issues/data/project/Project-1"

    # ═══════════════════════════════════════════════════════════════════════════
    # list_nodes_for_type with root_path Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__list_nodes_for_type__no_root_returns_all(self):                # No root = all nodes returned
        self.create_issue_at_path(".issues/data/bug/Bug-1/issue.json"                      , "bug" , "Bug-1" , "First bug" )
        self.create_issue_at_path(".issues/data/project/Project-1/issues/Bug-2/issue.json"  , "bug" , "Bug-2" , "Second bug")
        service   = Node__Service(repository=self.repository)
        summaries = service.list_nodes_for_type(Safe_Str__Node_Type("bug"))
        labels = [str(s.label) for s in summaries]
        assert "Bug-1" in labels
        assert "Bug-2" in labels
        assert len(summaries) == 2

    def test__list_nodes_for_type__with_root_filters(self):                  # Root path filters results
        self.create_issue_at_path(".issues/data/project/Project-1/issue.json"              , "project", "Project-1", "Project One")
        self.create_issue_at_path(".issues/data/project/Project-1/issues/Bug-1/issue.json" , "bug"    , "Bug-1"    , "Bug under project")
        self.create_issue_at_path(".issues/data/bug/Bug-2/issue.json"                      , "bug"    , "Bug-2"    , "Bug at top level")
        service   = Node__Service(repository=self.repository)
        root_path = Safe_Str__File__Path(".issues/data/project/Project-1")
        summaries = service.list_nodes_for_type(Safe_Str__Node_Type("bug"), root_path=root_path)
        labels = [str(s.label) for s in summaries]
        assert "Bug-1" in labels
        assert "Bug-2" not in labels
        assert len(summaries) == 1

    def test__list_nodes_for_type__filters_by_type(self):                    # Only returns matching type
        self.create_issue_at_path(".issues/data/bug/Bug-1/issue.json"  , "bug" , "Bug-1" , "A bug" )
        self.create_issue_at_path(".issues/data/task/Task-1/issue.json", "task", "Task-1", "A task")
        service   = Node__Service(repository=self.repository)
        summaries = service.list_nodes_for_type(Safe_Str__Node_Type("bug"))
        labels = [str(s.label) for s in summaries]
        assert "Bug-1"  in labels
        assert "Task-1" not in labels
        assert len(summaries) == 1

    def test__list_nodes_for_type__returns_summaries_with_correct_fields(self):
        self.create_issue_at_path(".issues/data/bug/Bug-1/issue.json", "bug", "Bug-1", "Test title")
        service   = Node__Service(repository=self.repository)
        summaries = service.list_nodes_for_type(Safe_Str__Node_Type("bug"))
        assert len(summaries)            == 1
        assert str(summaries[0].label)   == "Bug-1"
        assert str(summaries[0].title)   == "Test title"
        assert str(summaries[0].status)  == "backlog"

    # ═══════════════════════════════════════════════════════════════════════════
    # list_nodes (full integration) Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__list_nodes__no_root_service_returns_all(self):                  # Without root service, returns all
        self.create_issue_at_path(".issues/data/bug/Bug-1/issue.json"  , "bug" , "Bug-1" , "Bug")
        self.create_issue_at_path(".issues/data/task/Task-1/issue.json", "task", "Task-1", "Task")
        service  = Node__Service(repository=self.repository)
        response = service.list_nodes()
        assert response.success is True
        labels = [str(n.label) for n in response.nodes]
        assert "Bug-1"  in labels
        assert "Task-1" in labels

    def test__list_nodes__with_root_scoping(self):                            # Root scoping filters list_nodes
        self.create_issue_at_path(".issues/data/project/Project-1/issue.json"              , "project", "Project-1", "Project")
        self.create_issue_at_path(".issues/data/project/Project-1/issues/Task-1/issue.json", "task"   , "Task-1"   , "Scoped task")
        self.create_issue_at_path(".issues/data/task/Task-2/issue.json"                    , "task"   , "Task-2"   , "Unscoped task")
        self.create_issue_at_path(".issues/data/bug/Bug-1/issue.json"                      , "bug"    , "Bug-1"    , "Unscoped bug")
        mock_root              = Mock__Root__Selection__Service()
        mock_root.current_root = Safe_Str__File__Path(".issues/data/project/Project-1")
        service                = Node__Service(repository             = self.repository,
                                                root_selection_service = mock_root      )
        response = service.list_nodes()
        assert response.success is True
        labels = [str(n.label) for n in response.nodes]
        assert "Project-1" in labels
        assert "Task-1"    in labels
        assert "Task-2"    not in labels
        assert "Bug-1"     not in labels

    def test__list_nodes__with_root_scoping_by_type(self):                    # Root scoping + type filter
        self.create_issue_at_path(".issues/data/project/Project-1/issue.json"              , "project", "Project-1", "Project")
        self.create_issue_at_path(".issues/data/project/Project-1/issues/Task-1/issue.json", "task"   , "Task-1"   , "Scoped task")
        self.create_issue_at_path(".issues/data/project/Project-1/issues/Bug-1/issue.json" , "bug"    , "Bug-1"    , "Scoped bug")
        self.create_issue_at_path(".issues/data/task/Task-2/issue.json"                    , "task"   , "Task-2"   , "Unscoped task")
        mock_root              = Mock__Root__Selection__Service()
        mock_root.current_root = Safe_Str__File__Path(".issues/data/project/Project-1")
        service                = Node__Service(repository             = self.repository,
                                                root_selection_service = mock_root      )
        response = service.list_nodes(node_type=Safe_Str__Node_Type("task"))
        assert response.success is True
        labels = [str(n.label) for n in response.nodes]
        assert "Task-1"    in labels
        assert "Task-2"    not in labels
        assert "Bug-1"     not in labels
        assert "Project-1" not in labels

    def test__list_nodes__empty_root_returns_all(self):                       # Empty root = no filtering
        self.create_issue_at_path(".issues/data/bug/Bug-1/issue.json" , "bug" , "Bug-1" , "Bug")
        self.create_issue_at_path(".issues/data/task/Task-1/issue.json", "task", "Task-1", "Task")
        mock_root = Mock__Root__Selection__Service()
        service   = Node__Service(repository             = self.repository,
                                   root_selection_service = mock_root      )
        response = service.list_nodes()
        assert response.success is True
        labels = [str(n.label) for n in response.nodes]
        assert "Bug-1"  in labels
        assert "Task-1" in labels

    def test__list_nodes__deeply_nested_scoping(self):                        # Root scoping works with deep nesting
        self.create_issue_at_path(".issues/data/project/Project-1/issue.json",
                                  "project", "Project-1", "Project")
        self.create_issue_at_path(".issues/data/project/Project-1/issues/Task-1/issue.json",
                                  "task", "Task-1", "Task under project")
        self.create_issue_at_path(".issues/data/project/Project-1/issues/Task-1/issues/Bug-1/issue.json",
                                  "bug", "Bug-1", "Bug under task under project")
        self.create_issue_at_path(".issues/data/bug/Bug-2/issue.json",
                                  "bug", "Bug-2", "Top-level bug")
        mock_root              = Mock__Root__Selection__Service()
        mock_root.current_root = Safe_Str__File__Path(".issues/data/project/Project-1")
        service                = Node__Service(repository             = self.repository,
                                                root_selection_service = mock_root      )
        response = service.list_nodes()
        assert response.success is True
        labels = [str(n.label) for n in response.nodes]
        assert "Project-1" in labels
        assert "Task-1"    in labels
        assert "Bug-1"     in labels
        assert "Bug-2"     not in labels

    def test__list_nodes__response_total_matches_nodes_count(self):           # Verify total count
        self.create_issue_at_path(".issues/data/project/Project-1/issue.json"              , "project", "Project-1", "Project")
        self.create_issue_at_path(".issues/data/project/Project-1/issues/Task-1/issue.json", "task"   , "Task-1"   , "Task")
        mock_root              = Mock__Root__Selection__Service()
        mock_root.current_root = Safe_Str__File__Path(".issues/data/project/Project-1")
        service                = Node__Service(repository             = self.repository,
                                                root_selection_service = mock_root      )
        response = service.list_nodes()
        assert response.success is True
        assert response.total   == len(response.nodes)
        assert response.total   == 2
