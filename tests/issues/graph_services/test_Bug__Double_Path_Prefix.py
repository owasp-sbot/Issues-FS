# ═══════════════════════════════════════════════════════════════════════════════
# test_Bug__Double_Path_Prefix - Tests documenting the double .issues path bug
#
# BUG: When Graph__Repository__Factory.create_local_disk() is called with
#      root_path pointing to an .issues/ directory (as CLI__Context does),
#      the Path__Handler__Graph_Node still uses its default base_path='.issues'.
#      This causes all file operations to look in .issues/.issues/... instead
#      of .issues/...
#
# These tests PASS because they document the CURRENT (broken) behaviour.
# When the bug is fixed, these tests should be updated to reflect correct paths.
# ═══════════════════════════════════════════════════════════════════════════════

import json
import os
import shutil
import tempfile

from unittest                                                                           import TestCase
from memory_fs.storage_fs.providers.Storage_FS__Local_Disk                              import Storage_FS__Local_Disk
from issues_fs.issues.graph_services.Graph__Repository__Factory                         import Graph__Repository__Factory
from issues_fs.issues.graph_services.Graph__Repository                                  import Graph__Repository
from issues_fs.issues.storage.Path__Handler__Graph_Node                                 import Path__Handler__Graph_Node
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                      import Safe_Str__Node_Type, Safe_Str__Node_Label


class test_Bug__Double_Path_Prefix(TestCase):
    """Tests that document the double .issues path prefix bug.

    The bug: CLI discovers /repo/.issues/ and passes it as root_path to
    Graph__Repository__Factory.create_local_disk(). The factory creates
    Storage_FS__Local_Disk(root_path='/repo/.issues') but the path handler
    still uses base_path='.issues', causing all paths to resolve to
    /repo/.issues/.issues/... instead of /repo/.issues/...
    """

    @classmethod
    def setUpClass(cls):
        cls.temp_dir   = tempfile.mkdtemp()
        cls.issues_dir = os.path.join(cls.temp_dir, '.issues')
        os.makedirs(cls.issues_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 1: Path handler default always prepends .issues
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_bug__path_handler_default_base_path_is_dot_issues(self):                  # The default is '.issues'
        handler = Path__Handler__Graph_Node()
        assert str(handler.base_path) == '.issues'                                     # This is the root cause

    def test_bug__path_handler_prepends_dot_issues_to_config(self):                    # Config paths get .issues/ prefix
        handler = Path__Handler__Graph_Node()
        assert handler.path_for_node_types() == '.issues/config/node-types.json'       # BUG: should be 'config/node-types.json'
                                                                                       # when storage root is already .issues/

    def test_bug__path_handler_prepends_dot_issues_to_data(self):                      # Data paths get .issues/ prefix
        handler = Path__Handler__Graph_Node()
        path = handler.path_for_issue_json(node_type = Safe_Str__Node_Type('bug'),
                                           label     = Safe_Str__Node_Label('Bug-1'))
        assert path == '.issues/data/bug/Bug-1/issue.json'                             # BUG: should be 'data/bug/Bug-1/issue.json'

    def test_bug__path_handler_prepends_dot_issues_to_index(self):                     # Index paths get .issues/ prefix
        handler = Path__Handler__Graph_Node()
        assert handler.path_for_global_index() == '.issues/_index.json'                # BUG: should be '_index.json'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 2: Factory does NOT override the path handler's base_path
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_bug__factory_creates_path_handler_with_default_base_path(self):           # Factory uses default .issues base
        repo = Graph__Repository__Factory.create_local_disk(root_path=self.issues_dir)
        assert str(repo.path_handler.base_path) == '.issues'                           # BUG: should be '' or '.' since
                                                                                       # storage root is already .issues/

    def test_bug__factory_memory_backend_also_has_default_base_path(self):             # Memory backend has same default
        repo = Graph__Repository__Factory.create_memory()
        assert str(repo.path_handler.base_path) == '.issues'                           # Same default in all backends

    def test_bug__all_factory_methods_use_same_default(self):                          # All factory methods share the bug
        repo_local  = Graph__Repository__Factory.create_local_disk(root_path=self.issues_dir)
        repo_memory = Graph__Repository__Factory.create_memory()

        assert str(repo_local.path_handler.base_path)  == '.issues'
        assert str(repo_memory.path_handler.base_path) == '.issues'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 3: Storage root + path handler = doubled path
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_bug__effective_path_is_doubled(self):                                     # The combination doubles .issues
        repo = Graph__Repository__Factory.create_local_disk(root_path=self.issues_dir)
        storage_root  = repo.storage_fs.root_path                                      # e.g., /tmp/xxx/.issues
        handler_path  = repo.path_handler.path_for_node_types()                        # .issues/config/node-types.json

        effective_path = os.path.join(storage_root, handler_path)
        assert '/.issues/.issues/' in effective_path                                   # BUG: double .issues in path

    def test_bug__effective_config_path_does_not_exist_on_real_repo(self):              # Doubled path doesn't match real files
        # Create a real .issues/config/node-types.json at the correct location
        config_dir = os.path.join(self.issues_dir, 'config')
        os.makedirs(config_dir, exist_ok=True)
        types_file = os.path.join(config_dir, 'node-types.json')
        with open(types_file, 'w') as f:
            json.dump({'types': [{'name': 'bug', 'description': 'Bug report'}]}, f)

        # The file exists at the correct path
        assert os.path.exists(types_file) is True                                      # .issues/config/node-types.json exists

        # But the factory-created repo cannot see it
        repo = Graph__Repository__Factory.create_local_disk(root_path=self.issues_dir)
        loaded_types = repo.node_types_load()
        assert loaded_types == []                                                      # BUG: returns empty despite file existing

    def test_bug__effective_data_path_does_not_exist_on_real_repo(self):                # Real issue files are invisible
        # Create a real issue at the correct path
        issue_dir = os.path.join(self.issues_dir, 'data', 'bug', 'Bug-1')
        os.makedirs(issue_dir, exist_ok=True)
        issue_file = os.path.join(issue_dir, 'issue.json')
        with open(issue_file, 'w') as f:
            json.dump({'node_type': 'bug',
                        'label'    : 'Bug-1',
                        'title'    : 'A real bug',
                        'status'   : 'backlog'}, f)

        # The file exists at the correct path
        assert os.path.exists(issue_file) is True

        # But the repo cannot find it
        repo = Graph__Repository__Factory.create_local_disk(root_path=self.issues_dir)
        node = repo.node_load(node_type = Safe_Str__Node_Type('bug'),
                              label     = Safe_Str__Node_Label('Bug-1'))
        assert node is None                                                            # BUG: returns None for existing issue

    def test_bug__nodes_list_all_bypasses_path_handler(self):                         # nodes_list_all uses raw file scan
        # nodes_list_all() uses storage_fs.files__paths() which scans ALL files
        # under the storage root. It does NOT go through the path handler.
        # So it CAN find issues even though path-handler-based operations can't.
        test_issues = os.path.join(self.temp_dir, '.issues_list_all_test')
        os.makedirs(test_issues, exist_ok=True)

        issue_dir = os.path.join(test_issues, 'data', 'task', 'Task-1')
        os.makedirs(issue_dir, exist_ok=True)
        with open(os.path.join(issue_dir, 'issue.json'), 'w') as f:
            json.dump({'node_type': 'task',
                        'label'    : 'Task-1',
                        'title'    : 'A real task',
                        'status'   : 'backlog'}, f)

        repo  = Graph__Repository__Factory.create_local_disk(root_path=test_issues)
        nodes = repo.nodes_list_all()
        assert len(nodes) == 1                                                         # WORKS: raw scan finds the issue

        # But path-handler-based load CANNOT find the same issue
        node = repo.node_load(node_type=Safe_Str__Node_Type('task'),
                              label=Safe_Str__Node_Label('Task-1'))
        assert node is None                                                            # BUG: path handler doubles the path

        # Cleanup
        shutil.rmtree(test_issues)

    def test_bug__node_load_by_label_bypasses_path_handler(self):                     # label-based load also uses raw scan
        test_issues = os.path.join(self.temp_dir, '.issues_label_test')
        os.makedirs(test_issues, exist_ok=True)

        issue_dir = os.path.join(test_issues, 'data', 'bug', 'Bug-7')
        os.makedirs(issue_dir, exist_ok=True)
        with open(os.path.join(issue_dir, 'issue.json'), 'w') as f:
            json.dump({'node_type': 'bug',
                        'label'    : 'Bug-7',
                        'title'    : 'Found by label scan',
                        'status'   : 'backlog'}, f)

        repo = Graph__Repository__Factory.create_local_disk(root_path=test_issues)

        # node_load_by_label() uses files__paths() scanning → works
        by_label = repo.node_load_by_label(label=Safe_Str__Node_Label('Bug-7'))
        assert by_label is not None                                                    # WORKS: raw file scan
        assert by_label.title == 'Found by label scan'

        # node_load() uses path handler → broken
        by_type = repo.node_load(node_type=Safe_Str__Node_Type('bug'),
                                 label=Safe_Str__Node_Label('Bug-7'))
        assert by_type is None                                                         # BUG: path handler doubles path

        # Same issue, two APIs, different results
        # Cleanup
        shutil.rmtree(test_issues)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 4: Test-created data lands in .issues/.issues/... on disk
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_bug__factory_writes_to_doubled_path_on_disk(self):                        # Data written through factory lands in wrong place
        test_issues_dir = os.path.join(self.temp_dir, '.issues_write_test')
        os.makedirs(test_issues_dir, exist_ok=True)

        repo = Graph__Repository__Factory.create_local_disk(root_path=test_issues_dir)

        # Save node types through the repo
        from issues_fs.schemas.graph.Schema__Node__Type import Schema__Node__Type
        types = [Schema__Node__Type(name='bug', description='Bug report')]
        repo.node_types_save(types)

        # File should be at .issues_write_test/config/node-types.json (correct)
        correct_path = os.path.join(test_issues_dir, 'config', 'node-types.json')
        doubled_path = os.path.join(test_issues_dir, '.issues', 'config', 'node-types.json')

        assert os.path.exists(correct_path) is False                                   # BUG: NOT at the correct location
        assert os.path.exists(doubled_path) is True                                    # BUG: at the doubled location

        # Cleanup
        shutil.rmtree(test_issues_dir)

    def test_bug__factory_writes_issue_to_doubled_path_on_disk(self):                  # Issue data also lands in wrong place
        test_issues_dir = os.path.join(self.temp_dir, '.issues_issue_test')
        os.makedirs(test_issues_dir, exist_ok=True)

        repo = Graph__Repository__Factory.create_local_disk(root_path=test_issues_dir)

        from issues_fs.schemas.graph.Schema__Node import Schema__Node
        node = Schema__Node(node_type = 'bug',
                            label     = 'Bug-99',
                            title     = 'Test bug',
                            status    = 'backlog')
        repo.node_save(node)

        correct_path = os.path.join(test_issues_dir, 'data', 'bug', 'Bug-99', 'issue.json')
        doubled_path = os.path.join(test_issues_dir, '.issues', 'data', 'bug', 'Bug-99', 'issue.json')

        assert os.path.exists(correct_path) is False                                   # BUG: NOT at the correct location
        assert os.path.exists(doubled_path) is True                                    # BUG: at the doubled location

        # Cleanup
        shutil.rmtree(test_issues_dir)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 5: Round-trip through factory hides the bug (why existing tests pass)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_bug__round_trip_masks_the_bug(self):                                      # Write+read through factory works
        test_issues_dir = os.path.join(self.temp_dir, '.issues_roundtrip_test')
        os.makedirs(test_issues_dir, exist_ok=True)

        repo = Graph__Repository__Factory.create_local_disk(root_path=test_issues_dir)

        # Write types through factory
        from issues_fs.schemas.graph.Schema__Node__Type import Schema__Node__Type
        types = [Schema__Node__Type(name='bug', description='Bug report')]
        repo.node_types_save(types)

        # Read types through same factory → works! (both use doubled path)
        loaded = repo.node_types_load()
        assert len(loaded) == 1                                                        # Passes because read also uses doubled path
        assert loaded[0].name == 'bug'

        # Cleanup
        shutil.rmtree(test_issues_dir)

    def test_bug__round_trip_for_nodes_masks_the_bug(self):                            # Node save+load through factory works
        test_issues_dir = os.path.join(self.temp_dir, '.issues_node_rt_test')
        os.makedirs(test_issues_dir, exist_ok=True)

        repo = Graph__Repository__Factory.create_local_disk(root_path=test_issues_dir)

        from issues_fs.schemas.graph.Schema__Node import Schema__Node
        node = Schema__Node(node_type = 'bug',
                            label     = 'Bug-42',
                            title     = 'Round trip bug',
                            status    = 'backlog')
        repo.node_save(node)

        loaded = repo.node_load(node_type = Safe_Str__Node_Type('bug'),
                                label     = Safe_Str__Node_Label('Bug-42'))
        assert loaded is not None                                                      # Passes because both go through doubled path
        assert loaded.label == 'Bug-42'
        assert loaded.title == 'Round trip bug'

        # But the file is at the WRONG location on disk
        correct_path = os.path.join(test_issues_dir, 'data', 'bug', 'Bug-42', 'issue.json')
        doubled_path = os.path.join(test_issues_dir, '.issues', 'data', 'bug', 'Bug-42', 'issue.json')
        assert os.path.exists(correct_path) is False                                   # Not where you'd expect
        assert os.path.exists(doubled_path) is True                                    # At the wrong doubled location

        # Cleanup
        shutil.rmtree(test_issues_dir)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 6: CLI context discovery + factory = the full bug chain
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_bug__cli_discovery_returns_dot_issues_path(self):                         # CLI returns .issues/ as root
        from issues_fs_cli.cli.CLI__Context import CLI__Context                        # Import CLI context

        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)                                                    # cd to dir with .issues/
            ctx = CLI__Context.__new__(CLI__Context)                                   # Create without __init__
            root = ctx.discover_issues_root()
            assert root.endswith('.issues')                                             # Returns path ending in .issues
            assert root == self.issues_dir                                              # It's the full path
        finally:
            os.chdir(original_cwd)

    def test_bug__cli_discovery_path_fed_to_factory_creates_double_path(self):         # Full chain: discover → factory → doubled
        from issues_fs_cli.cli.CLI__Context import CLI__Context

        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            ctx = CLI__Context.__new__(CLI__Context)
            discovered_root = ctx.discover_issues_root()

            # This is what CLI__Context.__init__ does
            repo = Graph__Repository__Factory.create_local_disk(root_path=discovered_root)

            # Storage is rooted at .issues/
            assert discovered_root.endswith('.issues')

            # Path handler still prepends .issues/
            assert str(repo.path_handler.base_path) == '.issues'

            # So effective paths are doubled
            config_path = repo.path_handler.path_for_node_types()
            assert config_path == '.issues/config/node-types.json'                     # BUG: effective = .issues/.issues/...

        finally:
            os.chdir(original_cwd)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 7: Real .issues/ repos from the ecosystem are unreadable
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_bug__real_repo_split_behaviour(self):                                    # Simulate a real repo's .issues/
        real_issues = os.path.join(self.temp_dir, '.issues_real_repo')
        os.makedirs(real_issues, exist_ok=True)

        # Create structure matching real Issues-FS repos
        config_dir = os.path.join(real_issues, 'config')
        os.makedirs(config_dir, exist_ok=True)
        with open(os.path.join(config_dir, 'node-types.json'), 'w') as f:
            json.dump({'types': [
                {'name': 'bug',     'description': 'Bug report'     },
                {'name': 'task',    'description': 'Task'           },
                {'name': 'feature', 'description': 'Feature request'},
            ]}, f)
        with open(os.path.join(config_dir, 'link-types.json'), 'w') as f:
            json.dump({'link_types': [
                {'verb': 'blocks', 'inverse': 'blocked-by'},
            ]}, f)

        # Create real issues
        for i in range(1, 4):
            issue_dir = os.path.join(real_issues, 'data', 'bug', f'Bug-{i}')
            os.makedirs(issue_dir, exist_ok=True)
            with open(os.path.join(issue_dir, 'issue.json'), 'w') as f:
                json.dump({'node_type': 'bug',
                            'label'    : f'Bug-{i}',
                            'title'    : f'Real bug number {i}',
                            'status'   : 'backlog'}, f)

        for i in range(1, 3):
            issue_dir = os.path.join(real_issues, 'data', 'task', f'Task-{i}')
            os.makedirs(issue_dir, exist_ok=True)
            with open(os.path.join(issue_dir, 'issue.json'), 'w') as f:
                json.dump({'node_type': 'task',
                            'label'    : f'Task-{i}',
                            'title'    : f'Real task number {i}',
                            'status'   : 'backlog'}, f)

        # 5 real issues on disk
        assert os.path.exists(os.path.join(real_issues, 'data', 'bug', 'Bug-1', 'issue.json'))
        assert os.path.exists(os.path.join(real_issues, 'data', 'bug', 'Bug-2', 'issue.json'))
        assert os.path.exists(os.path.join(real_issues, 'data', 'bug', 'Bug-3', 'issue.json'))
        assert os.path.exists(os.path.join(real_issues, 'data', 'task', 'Task-1', 'issue.json'))
        assert os.path.exists(os.path.join(real_issues, 'data', 'task', 'Task-2', 'issue.json'))

        repo = Graph__Repository__Factory.create_local_disk(root_path=real_issues)

        # === Path-handler-based operations: ALL BROKEN ===
        node_types  = repo.node_types_load()
        link_types  = repo.link_types_load()
        bug_1       = repo.node_load(node_type=Safe_Str__Node_Type('bug'),
                                     label=Safe_Str__Node_Label('Bug-1'))
        bug_1_exist = repo.node_exists(node_type=Safe_Str__Node_Type('bug'),
                                       label=Safe_Str__Node_Label('Bug-1'))

        assert node_types  == []                                                       # BUG: 3 types defined, sees 0
        assert link_types  == []                                                       # BUG: 1 link type defined, sees 0
        assert bug_1       is None                                                     # BUG: Bug-1 exists, returns None
        assert bug_1_exist is False                                                    # BUG: Bug-1 exists, returns False

        # === Raw-scan-based operations: WORK (bypass path handler) ===
        all_nodes       = repo.nodes_list_all()
        bug_1_by_label  = repo.node_load_by_label(label=Safe_Str__Node_Label('Bug-1'))
        bug_1_path      = repo.node_find_path_by_label(label=Safe_Str__Node_Label('Bug-1'))

        assert len(all_nodes)      == 5                                                # WORKS: raw scan finds all 5 issues
        assert bug_1_by_label      is not None                                         # WORKS: label scan finds Bug-1
        assert bug_1_by_label.title == 'Real bug number 1'
        assert bug_1_path          is not None                                         # WORKS: path scan finds Bug-1

        # This is the core inconsistency: two APIs for the same data, different results
        # node_load(type, label) → None (uses path handler → doubled path)
        # node_load_by_label(label) → found (uses raw file scan)

        # Cleanup
        shutil.rmtree(real_issues)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 8: What correct behaviour would look like (base_path='')
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_bug__empty_base_path_would_fix_the_issue(self):                           # Demonstrates the fix direction
        real_issues = os.path.join(self.temp_dir, '.issues_fix_demo')
        os.makedirs(real_issues, exist_ok=True)

        config_dir = os.path.join(real_issues, 'config')
        os.makedirs(config_dir, exist_ok=True)
        with open(os.path.join(config_dir, 'node-types.json'), 'w') as f:
            json.dump({'types': [{'name': 'bug', 'description': 'Bug report'}]}, f)

        issue_dir = os.path.join(real_issues, 'data', 'bug', 'Bug-1')
        os.makedirs(issue_dir, exist_ok=True)
        with open(os.path.join(issue_dir, 'issue.json'), 'w') as f:
            json.dump({'node_type': 'bug',
                        'label'    : 'Bug-1',
                        'title'    : 'This should be visible',
                        'status'   : 'backlog'}, f)

        # Manually create repo with empty base_path (the fix)
        from memory_fs.Memory_FS import Memory_FS
        memory_fs            = Memory_FS()
        storage              = Storage_FS__Local_Disk(root_path=real_issues)
        memory_fs.storage_fs = storage
        path_handler         = Path__Handler__Graph_Node(base_path='.')                # Fix: use '.' instead of '.issues'

        repo = Graph__Repository(memory_fs=memory_fs, path_handler=path_handler)

        # NOW it can see the real files
        node_types = repo.node_types_load()
        all_nodes  = repo.nodes_list_all()
        bug_1      = repo.node_load(node_type=Safe_Str__Node_Type('bug'),
                                    label=Safe_Str__Node_Label('Bug-1'))

        assert len(node_types) == 1                                                    # Can see the type
        assert node_types[0].name == 'bug'
        assert len(all_nodes)  == 1                                                    # Can see the issue
        assert bug_1           is not None                                             # Can load the issue
        assert bug_1.title     == 'This should be visible'

        # Cleanup
        shutil.rmtree(real_issues)
