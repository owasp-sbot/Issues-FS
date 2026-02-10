# ═══════════════════════════════════════════════════════════════════════════════
# test_Graph__Repository__B10__Recursive_Discovery - Tests for Phase 2 B10
# Recursive node discovery via nodes_list_all(), SKIP_LABELS, is_path_under_root,
# extract_node_type_from_file, and updated nodes_list_labels
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                       import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                       import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                        import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                        import Timestamp_Now
from osbot_utils.utils.Json                                                                             import json_dumps
from issues_fs.schemas.graph.Safe_Str__Graph_Types               import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status
from issues_fs.schemas.graph.Schema__Node                        import Schema__Node
from issues_fs.schemas.graph.Schema__Node__Info                  import Schema__Node__Info
from issues_fs.issues.graph_services.Graph__Repository import Graph__Repository, SKIP_LABELS
from issues_fs.issues.storage.Path__Handler__Graph_Node  import Path__Handler__Graph_Node


class test_Graph__Repository__B10__Recursive_Discovery(TestCase):

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

    def write_raw_json_to_path(self, path: str, data: dict) -> None:             # Write raw JSON to storage
        content = json_dumps(data, indent=2)
        self.repository.storage_fs.file__save(path, content.encode('utf-8'))

    # ═══════════════════════════════════════════════════════════════════════════════
    # SKIP_LABELS Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__skip_labels__contains_system_folders(self):                         # Verify SKIP_LABELS has expected values
        skip = sorted(list(SKIP_LABELS))
        assert skip == ['.issues', 'config', 'data', 'indexes', 'issues']


    # ═══════════════════════════════════════════════════════════════════════════════
    # nodes_list_all Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__nodes_list_all__finds_top_level_issues(self):                      # Test discovery at top level
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json'  ,
                                     {'node_type': 'bug'  , 'label': 'Bug-1' })
        self.write_raw_json_to_path('.issues/data/task/Task-1/issue.json',
                                     {'node_type': 'task' , 'label': 'Task-1'})

        result = self.repository.nodes_list_all()

        labels = [str(n.label) for n in result]

        assert 'Bug-1'  in labels
        assert 'Task-1' in labels
        assert len(result) == 2

    def test__nodes_list_all__finds_nested_issues(self):                         # Test discovery in issues/ subfolders
        self.write_raw_json_to_path('.issues/data/project/Project-1/issue.json'                            ,
                                     {'node_type': 'project', 'label': 'Project-1'})
        self.write_raw_json_to_path('.issues/data/project/Project-1/issues/Task-1/issue.json'              ,
                                     {'node_type': 'task'   , 'label': 'Task-1'   })
        self.write_raw_json_to_path('.issues/data/project/Project-1/issues/Task-1/issues/Bug-1/issue.json' ,
                                     {'node_type': 'bug'    , 'label': 'Bug-1'    })

        result = self.repository.nodes_list_all()

        labels = [str(n.label) for n in result]

        assert 'Project-1' in labels
        assert 'Task-1'    in labels
        assert 'Bug-1'     in labels
        assert len(result) == 3

    def test__nodes_list_all__skips_system_folders(self):                         # Test that SKIP_LABELS are excluded
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json',
                                     {'node_type': 'bug', 'label': 'Bug-1'})
        self.write_raw_json_to_path('.issues/config/issue.json'        ,         # System folder should be skipped
                                     {'node_type': 'config'            })

        result = self.repository.nodes_list_all()

        labels = [str(n.label) for n in result]

        assert 'Bug-1'  in labels
        assert 'config' not in labels

    def test__nodes_list_all__ignores_node_json(self):                           # Test that node.json files are not found
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/node.json' ,
                                     {'node_type': 'bug', 'label': 'Bug-1'})

        result = self.repository.nodes_list_all()

        assert len(result) == 0

    def test__nodes_list_all__with_root_path_filter(self):                       # Test root_path filtering
        self.write_raw_json_to_path('.issues/data/project/Project-1/issue.json'                ,
                                     {'node_type': 'project', 'label': 'Project-1'})
        self.write_raw_json_to_path('.issues/data/project/Project-1/issues/Task-1/issue.json'  ,
                                     {'node_type': 'task'   , 'label': 'Task-1'   })
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json'                        ,
                                     {'node_type': 'bug'    , 'label': 'Bug-1'    })

        result = self.repository.nodes_list_all(root_path=Safe_Str__File__Path('.issues/data/project/Project-1'))

        labels = [str(n.label) for n in result]

        assert 'Project-1' in labels
        assert 'Task-1'    in labels
        assert 'Bug-1'     not in labels

    def test__nodes_list_all__returns_empty_for_empty_storage(self):             # Test empty storage
        result = self.repository.nodes_list_all()

        assert len(result) == 0

    def test__nodes_list_all__returns_schema_node_info(self):                    # Test return type
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json',
                                     {'node_type': 'bug', 'label': 'Bug-1'})

        result = self.repository.nodes_list_all()

        assert len(result) == 1
        assert type(result[0]) is Schema__Node__Info
        assert str(result[0].label)     == 'Bug-1'
        assert str(result[0].node_type) == 'bug'
        assert str(result[0].path)      == '.issues/data/bug/Bug-1'

    # ═══════════════════════════════════════════════════════════════════════════════
    # is_path_under_root Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__is_path_under_root__match(self):                                   # Test path is under root
        result = self.repository.is_path_under_root(
            file_path = Safe_Str__File__Path('.issues/data/bug/Bug-1/issue.json'),
            root_path = Safe_Str__File__Path('.issues/data')                     )

        assert result is True

    def test__is_path_under_root__no_match(self):                                # Test path not under root
        result = self.repository.is_path_under_root(
            file_path = Safe_Str__File__Path('.issues/data/bug/Bug-1/issue.json'),
            root_path = Safe_Str__File__Path('.issues/config')                   )

        assert result is False

    def test__is_path_under_root__empty_root_matches_all(self):                  # Test empty root matches everything
        result = self.repository.is_path_under_root(
            file_path = Safe_Str__File__Path('.issues/data/bug/Bug-1/issue.json'),
            root_path = Safe_Str__File__Path('')                                 )

        assert result is True

    # ═══════════════════════════════════════════════════════════════════════════════
    # extract_node_type_from_file Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__extract_node_type_from_file__valid(self):                          # Test extraction of node_type
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json',
                                     {'node_type': 'bug', 'label': 'Bug-1'})

        result = self.repository.extract_node_type_from_file(
            Safe_Str__File__Path('.issues/data/bug/Bug-1/issue.json'))

        assert result == 'bug'

    def test__extract_node_type_from_file__missing_key(self):                    # Test missing node_type key
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json',
                                     {'label': 'Bug-1'})

        result = self.repository.extract_node_type_from_file(
            Safe_Str__File__Path('.issues/data/bug/Bug-1/issue.json'))

        assert result == ''

    def test__extract_node_type_from_file__nonexistent_file(self):               # Test nonexistent file
        result = self.repository.extract_node_type_from_file(
            Safe_Str__File__Path('.issues/data/bug/Bug-999/issue.json'))

        assert result == ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # nodes_list_labels (updated) Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__nodes_list_labels__delegates_to_nodes_list_all(self):              # Test updated list_labels finds issue.json only
        self.write_raw_json_to_path('.issues/data/task/Task-1/issue.json',
                                     {'node_type': 'task', 'label': 'Task-1'})
        self.write_raw_json_to_path('.issues/data/task/Task-2/issue.json',
                                     {'node_type': 'task', 'label': 'Task-2'})
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json'  ,
                                     {'node_type': 'bug' , 'label': 'Bug-1' })

        task_labels = self.repository.nodes_list_labels(Safe_Str__Node_Type('task'))
        all_labels  = self.repository.nodes_list_labels()

        task_strs = [str(l) for l in task_labels]
        all_strs  = [str(l) for l in all_labels]

        assert 'Task-1' in task_strs
        assert 'Task-2' in task_strs
        assert 'Bug-1'  not in task_strs
        assert len(all_strs) == 3

    def test__nodes_list_labels__ignores_node_json(self):                        # Test that node.json is not discovered
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/node.json',
                                     {'node_type': 'bug', 'label': 'Bug-1'})

        labels = self.repository.nodes_list_labels(Safe_Str__Node_Type('bug'))

        assert len(labels) == 0
