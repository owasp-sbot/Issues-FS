# ═══════════════════════════════════════════════════════════════════════════════
# test_B13__Remove_Node_Json_Fallback - Tests for Phase 2 B13
# Verifies removal of node.json fallback from:
#   - Graph__Repository.get_issue_file_path
#   - Root__Selection__Service (is_valid_root, scan, count, load)
#   - Issue__Children__Service (parent_exists, scan_child_folders, load_child)
#   - Migration__Node_To_Issue_Json script
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                       import Safe_Str__File__Path
from osbot_utils.utils.Json                                                                             import json_dumps
from issues_fs.schemas.graph.Safe_Str__Graph_Types               import Safe_Str__Node_Type, Safe_Str__Node_Label
from issues_fs.issues.graph_services.Graph__Repository   import Graph__Repository
from issues_fs.issues.phase_1.Root__Selection__Service   import Root__Selection__Service
from issues_fs.issues.phase_1.Issue__Children__Service   import Issue__Children__Service
from issues_fs.issues.storage.Path__Handler__Graph_Node  import Path__Handler__Graph_Node
from issues_fs.scripts.migrate_node_to_issue_json        import Migration__Node_To_Issue_Json


class test_B13__Graph__Repository__No_Fallback(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup for all tests
        cls.memory_fs    = Memory_FS__In_Memory()
        cls.path_handler = Path__Handler__Graph_Node()
        cls.repository   = Graph__Repository(memory_fs    = cls.memory_fs   ,
                                             path_handler = cls.path_handler)

    def setUp(self):                                                             # Reset storage before each test
        self.repository.clear_storage()

    def write_raw_json_to_path(self, path: str, data: dict) -> None:             # Write raw JSON to storage
        content = json_dumps(data, indent=2)
        self.repository.storage_fs.file__save(path, content.encode('utf-8'))

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_issue_file_path - No node.json Fallback (B13)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_issue_file_path__returns_none_for_node_json_only(self):         # Test no fallback to node.json
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-1')

        path_node = self.path_handler.path_for_node_json(node_type, label)
        self.write_raw_json_to_path(path_node, {'title': 'Legacy'})

        result = self.repository.get_issue_file_path(node_type, label)

        assert result is None                                                    # B13: no fallback

    def test__get_issue_file_path__returns_issue_json(self):                     # Test issue.json still found
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-2')

        path_issue = self.path_handler.path_for_issue_json(node_type, label)
        self.write_raw_json_to_path(path_issue, {'title': 'Current'})

        result = self.repository.get_issue_file_path(node_type, label)

        assert result == path_issue

    def test__node_load__returns_none_for_node_json_only(self):                  # Test node_load no fallback
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-3')

        path_node = self.path_handler.path_for_node_json(node_type, label)
        self.write_raw_json_to_path(path_node, {'title': 'Legacy',
                                                 'node_type': 'bug',
                                                 'label': 'Bug-3' })

        loaded = self.repository.node_load(node_type, label)

        assert loaded is None                                                    # B13: no fallback

    def test__node_exists__false_for_node_json_only(self):                       # Test node_exists no fallback
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-4')

        path_node = self.path_handler.path_for_node_json(node_type, label)
        self.write_raw_json_to_path(path_node, {'title': 'Legacy'})

        assert self.repository.node_exists(node_type, label) is False            # B13: no fallback


class test_B13__Root__Selection__Service__No_Fallback(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup for all tests
        cls.memory_fs    = Memory_FS__In_Memory()
        cls.path_handler = Path__Handler__Graph_Node()
        cls.repository   = Graph__Repository(memory_fs    = cls.memory_fs   ,
                                             path_handler = cls.path_handler)
        cls.root_service = Root__Selection__Service(repository   = cls.repository  ,
                                                    path_handler = cls.path_handler)

    def setUp(self):                                                             # Reset storage before each test
        self.repository.clear_storage()

    def write_raw_json_to_path(self, path: str, data: dict) -> None:
        content = json_dumps(data, indent=2)
        self.repository.storage_fs.file__save(path, content.encode('utf-8'))

    # ═══════════════════════════════════════════════════════════════════════════════
    # is_valid_root - issue.json only (B13)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__is_valid_root__true_for_issue_json(self):                          # Test valid with issue.json
        self.write_raw_json_to_path('.issues/data/project/Project-1/issue.json',
                                     {'node_type': 'project'})

        result = self.root_service.is_valid_root('data/project/Project-1')

        assert result is True

    def test__is_valid_root__false_for_node_json_only(self):                     # Test invalid with only node.json
        self.write_raw_json_to_path('.issues/data/project/Project-1/node.json',
                                     {'node_type': 'project'})

        result = self.root_service.is_valid_root('data/project/Project-1')

        assert result is False                                                   # B13: no fallback

    # ═══════════════════════════════════════════════════════════════════════════════
    # scan_for_issue_folders - issue.json only (B13)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__scan_for_issue_folders__finds_issue_json(self):                    # Test finds issue.json folders
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json',
                                     {'node_type': 'bug'})

        folders = self.root_service.scan_for_issue_folders()

        assert len(folders) == 1
        assert '.issues/data/bug/Bug-1' in folders

    def test__scan_for_issue_folders__ignores_node_json(self):                   # Test ignores node.json folders
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/node.json',
                                     {'node_type': 'bug'})

        folders = self.root_service.scan_for_issue_folders()

        assert len(folders) == 0                                                 # B13: node.json ignored

    # ═══════════════════════════════════════════════════════════════════════════════
    # count_top_level_issues - issue.json only (B13)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__count_top_level_issues__counts_issue_json(self):                   # Test counts issue.json only
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json'  ,
                                     {'node_type': 'bug'})
        self.write_raw_json_to_path('.issues/data/task/Task-1/node.json' ,       # Should be ignored
                                     {'node_type': 'task'})

        count = self.root_service.count_top_level_issues()

        assert count == 1                                                        # Only issue.json counted

    # ═══════════════════════════════════════════════════════════════════════════════
    # count_children_in_folder - issue.json only (B13)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__count_children_in_folder__counts_issue_json(self):                 # Test counts issue.json children only
        self.write_raw_json_to_path(
            '.issues/data/project/Project-1/issues/Task-1/issue.json',
            {'node_type': 'task'})
        self.write_raw_json_to_path(
            '.issues/data/project/Project-1/issues/Task-2/node.json' ,           # Should be ignored
            {'node_type': 'task'})

        count = self.root_service.count_children_in_folder('.issues/data/project/Project-1')

        assert count == 1                                                        # Only issue.json counted

    # ═══════════════════════════════════════════════════════════════════════════════
    # load_issue_summary - issue.json only (B13)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__load_issue_summary__loads_issue_json(self):                        # Test loads issue.json
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/issue.json',
                                     {'node_type': 'bug', 'title': 'Issue Bug'})

        data = self.root_service.load_issue_summary('.issues/data/bug/Bug-1')

        assert data               is not None
        assert data.get('title')  == 'Issue Bug'

    def test__load_issue_summary__returns_none_for_node_json_only(self):         # Test no fallback to node.json
        self.write_raw_json_to_path('.issues/data/bug/Bug-1/node.json',
                                     {'node_type': 'bug', 'title': 'Legacy'})

        data = self.root_service.load_issue_summary('.issues/data/bug/Bug-1')

        assert data is None                                                      # B13: no fallback


class test_B13__Issue__Children__Service__No_Fallback(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup for all tests
        cls.memory_fs        = Memory_FS__In_Memory()
        cls.path_handler     = Path__Handler__Graph_Node()
        cls.repository       = Graph__Repository(memory_fs    = cls.memory_fs   ,
                                                 path_handler = cls.path_handler)
        cls.children_service = Issue__Children__Service(repository   = cls.repository  ,
                                                        path_handler = cls.path_handler)

    def setUp(self):                                                             # Reset storage before each test
        self.repository.clear_storage()

    def write_raw_json_to_path(self, path: str, data: dict) -> None:
        content = json_dumps(data, indent=2)
        self.repository.storage_fs.file__save(path, content.encode('utf-8'))

    # ═══════════════════════════════════════════════════════════════════════════════
    # parent_exists - issue.json only (B13)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__parent_exists__true_for_issue_json(self):                          # Test parent with issue.json
        self.write_raw_json_to_path('.issues/data/project/Project-1/issue.json',
                                     {'node_type': 'project'})

        result = self.children_service.parent_exists('.issues/data/project/Project-1')

        assert result is True

    def test__parent_exists__false_for_node_json_only(self):                     # Test parent with only node.json
        self.write_raw_json_to_path('.issues/data/project/Project-1/node.json',
                                     {'node_type': 'project'})

        result = self.children_service.parent_exists('.issues/data/project/Project-1')

        assert result is False                                                   # B13: no fallback

    # ═══════════════════════════════════════════════════════════════════════════════
    # scan_child_folders - issue.json only (B13)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__scan_child_folders__finds_issue_json(self):                        # Test finds children with issue.json
        self.write_raw_json_to_path(
            '.issues/data/project/Project-1/issues/Task-1/issue.json',
            {'node_type': 'task'})

        folders = self.children_service.scan_child_folders(
            Safe_Str__File__Path('.issues/data/project/Project-1/issues'))

        assert len(folders) == 1

    def test__scan_child_folders__ignores_node_json(self):                       # Test ignores children with only node.json
        self.write_raw_json_to_path(
            '.issues/data/project/Project-1/issues/Task-1/node.json',
            {'node_type': 'task'})

        folders = self.children_service.scan_child_folders(
            Safe_Str__File__Path('.issues/data/project/Project-1/issues'))

        assert len(folders) == 0                                                 # B13: node.json ignored

    # ═══════════════════════════════════════════════════════════════════════════════
    # load_child_summary - issue.json only (B13)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__load_child_summary__loads_issue_json(self):                        # Test loads child from issue.json
        self.write_raw_json_to_path(
            '.issues/data/project/Project-1/issues/Task-1/issue.json',
            {'node_type': 'task', 'title': 'Child Task'})

        data = self.children_service.load_child_summary(
            '.issues/data/project/Project-1/issues/Task-1')

        assert data              is not None
        assert data.get('title') == 'Child Task'

    def test__load_child_summary__returns_none_for_node_json_only(self):         # Test no fallback to node.json
        self.write_raw_json_to_path(
            '.issues/data/project/Project-1/issues/Task-1/node.json',
            {'node_type': 'task', 'title': 'Legacy Task'})

        data = self.children_service.load_child_summary(
            '.issues/data/project/Project-1/issues/Task-1')

        assert data is None                                                      # B13: no fallback


class test_B13__Migration__Node_To_Issue_Json(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup for all tests
        cls.memory_fs = Memory_FS__In_Memory()

    def setUp(self):                                                             # Reset storage before each test
        self.memory_fs.storage_fs.clear()

    def write_raw_bytes_to_path(self, path: str, data: dict) -> None:
        content = json_dumps(data, indent=2)
        self.memory_fs.storage_fs.file__save(path, content.encode('utf-8'))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Migration run() Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__run__converts_node_json_to_issue_json(self):                       # Test conversion when no issue.json
        self.write_raw_bytes_to_path('data/bug/Bug-1/node.json',
                                      {'node_type': 'bug', 'title': 'Bug One'})

        migration = Migration__Node_To_Issue_Json(storage_fs=self.memory_fs.storage_fs)
        results   = migration.run()

        assert results['converted'] == 1
        assert results['deleted']   == 0

        assert self.memory_fs.storage_fs.file__exists('data/bug/Bug-1/issue.json') is True
        assert self.memory_fs.storage_fs.file__exists('data/bug/Bug-1/node.json')  is False

    def test__run__deletes_node_json_when_issue_json_exists(self):               # Test deletion when both exist
        self.write_raw_bytes_to_path('data/bug/Bug-2/node.json'  ,
                                      {'node_type': 'bug', 'title': 'Old'})
        self.write_raw_bytes_to_path('data/bug/Bug-2/issue.json' ,
                                      {'node_type': 'bug', 'title': 'New'})

        migration = Migration__Node_To_Issue_Json(storage_fs=self.memory_fs.storage_fs)
        results   = migration.run()

        assert results['converted'] == 0
        assert results['deleted']   == 1

        assert self.memory_fs.storage_fs.file__exists('data/bug/Bug-2/issue.json') is True
        assert self.memory_fs.storage_fs.file__exists('data/bug/Bug-2/node.json')  is False

    def test__run__no_changes_when_no_node_json(self):                           # Test no-op when no node.json
        self.write_raw_bytes_to_path('data/bug/Bug-3/issue.json',
                                      {'node_type': 'bug', 'title': 'Current'})

        migration = Migration__Node_To_Issue_Json(storage_fs=self.memory_fs.storage_fs)
        results   = migration.run()

        assert results['converted'] == 0
        assert results['deleted']   == 0

    def test__run__handles_multiple_files(self):                                 # Test multiple files at once
        self.write_raw_bytes_to_path('data/bug/Bug-1/node.json'  ,
                                      {'node_type': 'bug'})
        self.write_raw_bytes_to_path('data/task/Task-1/node.json',
                                      {'node_type': 'task'})
        self.write_raw_bytes_to_path('data/task/Task-2/node.json',
                                      {'node_type': 'task'})
        self.write_raw_bytes_to_path('data/task/Task-2/issue.json',
                                      {'node_type': 'task'})

        migration = Migration__Node_To_Issue_Json(storage_fs=self.memory_fs.storage_fs)
        results   = migration.run()

        assert results['converted'] == 2                                         # Bug-1 and Task-1
        assert results['deleted']   == 1                                         # Task-2 (had both)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Migration dry_run() Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__dry_run__reports_conversion_needed(self):                           # Test dry run reports conversions
        self.write_raw_bytes_to_path('data/bug/Bug-1/node.json',
                                      {'node_type': 'bug'})

        migration = Migration__Node_To_Issue_Json(storage_fs=self.memory_fs.storage_fs)
        results   = migration.dry_run()

        assert len(results['to_convert']) == 1
        assert len(results['to_delete'])  == 0
        assert 'data/bug/Bug-1/node.json' in results['to_convert']

    def test__dry_run__reports_deletion_needed(self):                             # Test dry run reports deletions
        self.write_raw_bytes_to_path('data/bug/Bug-1/node.json' ,
                                      {'node_type': 'bug'})
        self.write_raw_bytes_to_path('data/bug/Bug-1/issue.json',
                                      {'node_type': 'bug'})

        migration = Migration__Node_To_Issue_Json(storage_fs=self.memory_fs.storage_fs)
        results   = migration.dry_run()

        assert len(results['to_convert']) == 0
        assert len(results['to_delete'])  == 1
        assert 'data/bug/Bug-1/node.json' in results['to_delete']

    def test__dry_run__does_not_modify_files(self):                              # Test dry run is non-destructive
        self.write_raw_bytes_to_path('data/bug/Bug-1/node.json',
                                      {'node_type': 'bug'})

        migration = Migration__Node_To_Issue_Json(storage_fs=self.memory_fs.storage_fs)
        migration.dry_run()

        assert self.memory_fs.storage_fs.file__exists('data/bug/Bug-1/node.json')  is True  # Not deleted
        assert self.memory_fs.storage_fs.file__exists('data/bug/Bug-1/issue.json') is False  # Not created
