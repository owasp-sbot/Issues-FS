# ═══════════════════════════════════════════════════════════════════════════════
# test_Root__Selection__Service - Tests for Phase 1 root selection functionality
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from osbot_utils.utils.Json                                                                             import json_dumps
from issues_fs.schemas.issues.phase_1.Schema__Root                     import Schema__Root__Select__Request
from issues_fs.issues.graph_services.Graph__Repository         import Graph__Repository
from issues_fs.issues.phase_1.Root__Selection__Service         import Root__Selection__Service
from issues_fs.issues.storage.Path__Handler__Graph_Node        import Path__Handler__Graph_Node


class test_Root__Selection__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup for all tests
        cls.memory_fs    = Memory_FS__In_Memory()
        cls.path_handler = Path__Handler__Graph_Node()
        cls.repository   = Graph__Repository(memory_fs    = cls.memory_fs   ,
                                             path_handler = cls.path_handler)
        cls.service      = Root__Selection__Service(repository   = cls.repository  ,
                                                    path_handler = cls.path_handler)

    def setUp(self):                                                             # Reset storage before each test
        self.repository.clear_storage()
        self.service.current_root = ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def create_issue_at_path(self                             ,                  # Create issue file at path
                             path       : str                 ,
                             label      : str = 'Test-1'      ,
                             title      : str = 'Test Issue'  ,
                             node_type  : str = 'task'
                        ) -> None:
        data    = {'label': label, 'title': title, 'node_type': node_type}
        content = json_dumps(data, indent=2)
        self.repository.storage_fs.file__save(path, content.encode('utf-8'))

    def create_standard_issue(self                              ,                # Create issue in standard location
                              node_type  : str = 'task'         ,
                              label      : str = 'Task-1'       ,
                              title      : str = 'Test Task'
                         ) -> str:
        path = f".issues/data/{node_type}/{label}/issue.json"
        self.create_issue_at_path(path, label=label, title=title, node_type=node_type)
        return f".issues/data/{node_type}/{label}"

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_available_roots Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_available_roots__always_includes_root(self):                   # Test .issues/ is always included
        response = self.service.get_available_roots()

        assert response.success    is True
        assert int(response.total) >= 1
        assert len(response.roots) >= 1
        assert response.roots[0].path == ''                                      # Root has empty path

    def test__get_available_roots__finds_issues(self):                           # Test finds issue folders
        self.create_standard_issue(node_type='task', label='Task-1')
        self.create_standard_issue(node_type='bug',  label='Bug-1')

        response = self.service.get_available_roots()

        assert response.success    is True
        assert int(response.total) >= 3                                          # Root + 2 issues

        paths = [str(r.path) for r in response.roots]
        assert 'data/task/Task-1' in paths
        assert 'data/bug/Bug-1'   in paths

    def test__get_available_roots__includes_metadata(self):                      # Test candidates have metadata
        self.create_standard_issue(node_type='feature', label='Feature-1', title='My Feature')

        response = self.service.get_available_roots()

        feature_root = None
        for root in response.roots:
            if 'Feature-1' in str(root.path):
                feature_root = root
                break

        assert feature_root                  is not None
        assert str(feature_root.label)       == 'Feature-1'
        assert str(feature_root.title)       == 'My Feature'
        assert str(feature_root.issue_type)  == 'feature'

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_roots_with_children Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_roots_with_children__empty_when_no_issues_folders(self):       # Test no children folders
        self.create_standard_issue(node_type='task', label='Task-1')

        response = self.service.get_roots_with_children()

        assert response.success is True
        assert int(response.total) == 0                                          # No issues/ folders yet

    def test__get_roots_with_children__finds_parents(self):                      # Test finds folders with issues/
        self.create_standard_issue(node_type='feature', label='Feature-1')       # Create parent

        child_path = ".issues/data/feature/Feature-1/issues/Task-1/issue.json"   # Create child in issues/ folder
        self.create_issue_at_path(child_path, label='Task-1', node_type='task')

        response = self.service.get_roots_with_children()

        assert response.success    is True
        assert int(response.total) >= 1

        has_feature = any('Feature-1' in str(r.path) for r in response.roots)
        assert has_feature is True

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_current_root Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_current_root__default_is_root(self):                           # Test default current root
        response = self.service.get_current_root()

        assert response.success is True
        assert str(response.path) == ''
        assert str(response.label) == 'Root'

    def test__get_current_root__after_selection(self):                           # Test after selecting a root
        folder_path = self.create_standard_issue(node_type='feature', label='Feature-1')
        relative_path = 'data/feature/Feature-1'

        select_req = Schema__Root__Select__Request(path=relative_path)
        self.service.set_current_root(select_req)

        response = self.service.get_current_root()

        assert response.success          is True
        assert str(response.path)        == relative_path
        assert str(response.label)       == 'Feature-1'
        assert str(response.issue_type)  == 'feature'

    # ═══════════════════════════════════════════════════════════════════════════════
    # set_current_root Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__set_current_root__valid_path(self):                                # Test selecting valid root
        folder_path = self.create_standard_issue(node_type='task', label='Task-1')
        relative_path = 'data/task/Task-1'

        request  = Schema__Root__Select__Request(path=relative_path)
        response = self.service.set_current_root(request)

        assert response.success         is True
        assert str(response.path)       == relative_path
        assert str(response.previous)   == ''                                    # Was default root

    def test__set_current_root__invalid_path(self):                              # Test selecting invalid root
        request  = Schema__Root__Select__Request(path='nonexistent/path')
        response = self.service.set_current_root(request)

        assert response.success is False
        assert 'Invalid' in str(response.message)

    def test__set_current_root__empty_resets_to_default(self):                   # Test empty path is valid
        self.create_standard_issue(node_type='task', label='Task-1')             # Set a root first
        request1 = Schema__Root__Select__Request(path='data/task/Task-1')
        self.service.set_current_root(request1)

        request2 = Schema__Root__Select__Request(path='')                        # Reset to default
        response = self.service.set_current_root(request2)

        assert response.success       is True
        assert response.path          == ''
        assert response.previous      == 'data/task/Task-1'

    def test__set_current_root__tracks_previous(self):                           # Test previous root tracking
        self.create_standard_issue(node_type='task', label='Task-1')
        self.create_standard_issue(node_type='bug',  label='Bug-1')

        request1 = Schema__Root__Select__Request(path='data/task/Task-1')        # Select first
        self.service.set_current_root(request1)

        request2 = Schema__Root__Select__Request(path='data/bug/Bug-1')          # Select second
        response = self.service.set_current_root(request2)

        assert response.success        is True
        assert str(response.path)      == 'data/bug/Bug-1'
        assert str(response.previous)  == 'data/task/Task-1'

    # ═══════════════════════════════════════════════════════════════════════════════
    # is_valid_root Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__is_valid_root__empty_is_valid(self):                               # Test empty path is valid
        assert self.service.is_valid_root('') is True

    def test__is_valid_root__base_path_is_valid(self):                           # Test .issues/ is valid
        assert self.service.is_valid_root('.issues') is True

    def test__is_valid_root__with_issue_json(self):                              # Test folder with issue.json
        self.create_issue_at_path('.issues/data/task/Task-1/issue.json')

        assert self.service.is_valid_root('.issues/data/task/Task-1') is True

    def test__is_valid_root__false_for_node_json_only(self):                     # Phase 2 (B13): No node.json fallback
        self.create_issue_at_path('.issues/data/bug/Bug-1/node.json')

        assert self.service.is_valid_root('.issues/data/bug/Bug-1') is False     # Phase 2 (B13): No fallback

    def test__is_valid_root__without_issue_file(self):                           # Test folder without issue file
        assert self.service.is_valid_root('.issues/data/task/NoIssue') is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Root with issue.json Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__root_with_issue_json__uses_metadata(self):                         # Test root issue.json is read
        root_path = 'issue.json'
        self.create_issue_at_path(root_path                  ,
                                  label     = 'Gitrepo-1'    ,
                                  title     = 'My Project'   ,
                                  node_type = 'git-repo'     )

        response = self.service.get_available_roots()
        root = response.roots[0]

        assert str(root.label)      == 'Gitrepo-1'
        assert str(root.title)      == 'My Project'
        assert str(root.issue_type) == 'git-repo'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Depth Calculation Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__calculate_depth__root_is_zero(self):                               # Test root depth is 0
        depth = self.service.calculate_depth('.issues')
        assert depth == 0

    def test__calculate_depth__top_level_issue(self):                            # Test top-level issue depth
        depth = self.service.calculate_depth('.issues/data/task/Task-1')
        assert depth == 0                                                        # data/{type}/{label} = depth 0

    def test__calculate_depth__nested_issue(self):                               # Test nested issue depth
        depth = self.service.calculate_depth('.issues/data/feature/Feature-1/issues/Task-1')
        assert depth == 1                                                        # One issues/ segment

    def test__calculate_depth__deeply_nested(self):                              # Test deeply nested depth
        path = '.issues/data/feature/Feature-1/issues/Task-1/issues/Bug-1'
        depth = self.service.calculate_depth(path)
        assert depth == 2                                                        # Two issues/ segments

    # ═══════════════════════════════════════════════════════════════════════════════
    # Child Count Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__count_top_level_issues__counts_all_types(self):                    # Test counting top-level issues
        self.create_standard_issue(node_type='task',    label='Task-1')
        self.create_standard_issue(node_type='task',    label='Task-2')
        self.create_standard_issue(node_type='bug',     label='Bug-1')
        self.create_standard_issue(node_type='feature', label='Feature-1')

        count = self.service.count_top_level_issues()
        assert count == 4

    def test__count_children_in_folder__counts_nested(self):                     # Test counting children
        parent = ".issues/data/feature/Feature-1/issue.json"                     # Create parent
        self.create_issue_at_path(parent, label='Feature-1', node_type='feature')

        child1 = ".issues/data/feature/Feature-1/issues/Task-1/issue.json"       # Create children
        child2 = ".issues/data/feature/Feature-1/issues/Task-2/issue.json"
        self.create_issue_at_path(child1, label='Task-1', node_type='task')
        self.create_issue_at_path(child2, label='Task-2', node_type='task')

        count = self.service.count_children_in_folder('.issues/data/feature/Feature-1')
        assert count == 2

    def test__has_children_in_candidate(self):                                   # Test has_children in response
        parent = ".issues/data/feature/Feature-1/issue.json"
        self.create_issue_at_path(parent, label='Feature-1', node_type='feature')

        child1 = ".issues/data/feature/Feature-1/issues/Task-1/issue.json"
        child2 = ".issues/data/feature/Feature-1/issues/Bug-1/issue.json"
        self.create_issue_at_path(child1, label='Task-1', node_type='task')
        self.create_issue_at_path(child2, label='Bug-1',  node_type='bug')

        response = self.service.get_available_roots()

        feature_root = None
        for root in response.roots:
            if 'Feature-1' in str(root.path):
                feature_root = root
                break

        assert feature_root                    is not None
        assert feature_root.has_issues         is True
        assert int(feature_root.has_children)  == 2