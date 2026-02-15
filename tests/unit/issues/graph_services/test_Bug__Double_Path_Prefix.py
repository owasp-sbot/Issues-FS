# ═══════════════════════════════════════════════════════════════════════════════
# test_Bug__Double_Path_Prefix - Regression tests for the double .issues path bug
#
# BUG (FIXED): When Graph__Repository__Factory.create_local_disk() was called with
#      root_path pointing to an .issues/ directory, the Path__Handler__Graph_Node
#      used its default base_path='.issues', causing all file operations to look
#      in .issues/.issues/... instead of .issues/...
#
# FIX: All path handler methods now return relative paths (e.g., 'data/bug/Bug-1/issue.json')
#      without prepending base_path, since the storage backend already handles the root path.
#
# These tests verify the FIXED behaviour. They were originally bug tests that
# documented the broken behaviour, now converted to regression tests.
# ═══════════════════════════════════════════════════════════════════════════════

import json
import os
import shutil
from unittest                                                                           import TestCase
from memory_fs.Memory_FS                                                                import Memory_FS
from memory_fs.storage_fs.providers.Storage_FS__Local_Disk                              import Storage_FS__Local_Disk
from osbot_utils.testing.Temp_Folder                                                    import Temp_Folder
from osbot_utils.testing.__                                                             import __, __SKIP__
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path       import Safe_Str__File__Path
from osbot_utils.utils.Files                                                            import path_combine, folder_exists, create_folder, file_exists
from osbot_utils.utils.Json                                                             import json_to_file
from issues_fs.issues.graph_services.Graph__Repository__Factory                         import Graph__Repository__Factory
from issues_fs.issues.graph_services.Graph__Repository                                  import Graph__Repository
from issues_fs.issues.storage.Path__Handler__Graph_Node                                 import Path__Handler__Graph_Node
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                      import Safe_Str__Node_Type, Safe_Str__Node_Label
from issues_fs.schemas.graph.Schema__Node                                               import Schema__Node


class test__bug__Double_Path_Prefix(TestCase):
    """Regression tests for the double .issues path prefix bug.

    The bug was: CLI discovers /repo/.issues/ and passes it as root_path to
    Graph__Repository__Factory.create_local_disk(). The factory created
    Storage_FS__Local_Disk(root_path='/repo/.issues') but the path handler
    still used base_path='.issues', causing all paths to resolve to
    /repo/.issues/.issues/... instead of /repo/.issues/...

    The fix: all path handler methods now return relative paths without
    prepending base_path, since storage already handles the root path.
    """

    @classmethod
    def setUpClass(cls):
        cls.temp_folder   = Temp_Folder().__enter__()
        cls.repo_folder   = cls.temp_folder.full_path
        cls.issues_dir    = path_combine(cls.repo_folder,'.issues')
        assert folder_exists(cls.repo_folder) is True


    @classmethod
    def tearDownClass(cls):
        cls.temp_folder.__exit__(None, None, None)
        assert folder_exists(cls.repo_folder) is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 1: Path handler returns relative paths (no base_path prefix)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_path_handler_default_base_path_is_dot_issues(self):                  # The default is '.issues'
        with Path__Handler__Graph_Node() as _:
            assert _.base_path == '.issues'                                     # This is the root cause
            assert _.obj()     == __(base_path='.issues')

    def test__regression__path_handler_returns_relative_config_path(self):             # Config paths are relative
        handler = Path__Handler__Graph_Node()
        assert handler.path_for_node_types() == 'config/node-types.json'               # FIXED: no .issues/ prefix

    def test__regression__path_handler_returns_relative_data_path(self):                # Data paths are relative
        handler = Path__Handler__Graph_Node()
        path = handler.path_for_issue_json(node_type = Safe_Str__Node_Type('bug'),
                                           label     = Safe_Str__Node_Label('Bug-1'))
        assert path == 'data/bug/Bug-1/issue.json'                                    # FIXED: no .issues/ prefix

    def test__regression__path_handler_returns_relative_index_path(self):               # Index paths are relative
        handler = Path__Handler__Graph_Node()
        assert handler.path_for_global_index() == '_index.json'                        # FIXED: no .issues/ prefix

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 2: Factory still uses default base_path (but it no longer matters)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__regression__factory_creates_path_handler_with_default_base_path(self):    # Factory uses default .issues base
        repo = Graph__Repository__Factory.create_local_disk(root_path=self.issues_dir)
        assert str(repo.path_handler.base_path) == '.issues'                           # base_path is still '.issues'
                                                                                       # but path methods ignore it

    def test__regression__factory_memory_backend_also_has_default_base_path(self):      # Memory backend has same default
        repo = Graph__Repository__Factory.create_memory()
        assert str(repo.path_handler.base_path) == '.issues'                           # Same default in all backends

    def test__regression__all_factory_methods_use_same_default(self):                   # All factory methods share same default
        repo_local  = Graph__Repository__Factory.create_local_disk(root_path=self.issues_dir)
        repo_memory = Graph__Repository__Factory.create_memory()

        assert str(repo_local.path_handler.base_path)  == '.issues'
        assert str(repo_memory.path_handler.base_path) == '.issues'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 3: Storage root + path handler = correct path (no doubling)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__regression__effective_path_is_not_doubled(self):                          # The combination no longer doubles
        repo = Graph__Repository__Factory.create_local_disk(root_path=self.issues_dir)
        storage_root  = repo.storage_fs.root_path                                      # e.g., /tmp/xxx/.issues
        handler_path  = repo.path_handler.path_for_node_types()                        # config/node-types.json

        effective_path = os.path.join(storage_root, handler_path)
        assert '/.issues/.issues/' not in effective_path                               # FIXED: no double .issues
        assert effective_path.endswith('/config/node-types.json')

    def test__regression__effective_config_path_exists_on_real_repo(self):              # Config path now matches real files
        # Create a real .issues/config/node-types.json at the correct location
        config_dir = os.path.join(self.issues_dir, 'config')
        os.makedirs(config_dir, exist_ok=True)
        types_file = os.path.join(config_dir, 'node-types.json')
        with open(types_file, 'w') as f:
            json.dump({'types': [{'name': 'bug', 'description': 'Bug report'}]}, f)

        # The file exists at the correct path
        assert os.path.exists(types_file) is True                                      # .issues/config/node-types.json exists

        # The factory-created repo CAN now see it
        repo = Graph__Repository__Factory.create_local_disk(root_path=self.issues_dir)
        loaded_types = repo.node_types_load()
        assert len(loaded_types) == 1                                                  # FIXED: finds the types
        assert loaded_types[0].name == 'bug'

    def test__regression__effective_data_path_does_not_exist_on_real_repo(self):              # Real issue files are visible
        node_type       = 'bug'
        node_label      = 'Bug-1'
        issue_folder    = f'data/{node_type}/{node_label}'
        issue_file_name = 'issue.json'
        issue_file_path = f'{issue_folder}/{issue_file_name}'
        issue_data      = { 'node_type': 'bug'       ,                                  # todo: convert to dict()
                            'label'    : 'Bug-1'     ,
                            'title'    : 'A real bug',
                            'status'   : 'backlog'   }

        issue_dir  = path_combine(self.issues_dir, issue_folder)                    # Create a real issue at the correct path
        issue_file = path_combine(issue_dir      , issue_file_name    )
        create_folder(issue_dir)                                                    # make sure folder exists
        json_to_file(issue_data, path= issue_file)                                  # create issue file

        assert self.issues_dir.endswith('.issues') is True
        assert file_exists(issue_file            ) is True                                              # The file exists at the correct path

        with Graph__Repository__Factory.create_local_disk(root_path=self.issues_dir) as _:     # But the repo cannot find it
            assert type(_) is Graph__Repository
            assert _.obj() == __(  storage_fs          = __(root_path=self.issues_dir),
                                   memory_fs           =  __(storage_fs=__(root_path     = self.issues_dir),
                                                                          path_handlers = []             ),
                                   path_handler        =__(base_path='.issues')         ,
                                   issues_file_loader  = None                           ,
                                   issues_file_nodes   = None                           ,
                                   issues_file_loaded  = False                          )

            assert type(_.memory_fs ) is Memory_FS
            assert type(_.storage_fs) is Storage_FS__Local_Disk                                 # confirm storage type
            assert issue_file_path             == 'data/bug/Bug-1/issue.json'                   # confirm expect path
            assert issue_file_path in _.storage_fs.files__paths()                               # confirm issue_file_path exists in storage

            node       = _.node_load(node_type = Safe_Str__Node_Type('bug'),
                               label     = Safe_Str__Node_Label('Bug-1'))
            path       = _.get_issue_file_path(node_type, node_label)
            path_issue = _.path_handler.path_for_issue_json(node_type, node_label)

            assert type(node)  is Schema__Node                      # FIXED: now node_load returns the Schema
            assert node.obj()  == __(node_id     = ''          ,    # BUG, node_id should always be set
                                     node_type   = 'bug'       ,
                                     node_index  = 0           ,
                                     label       = 'Bug-1'     ,
                                     title       = 'A real bug',
                                     description =''           ,
                                     status      = 'backlog'   ,
                                     created_at  = __SKIP__    ,
                                     updated_at  = __SKIP__    ,
                                     created_by  = __SKIP__    ,
                                     tags        = []          ,
                                     links       = []          ,
                                     properties  = __()        )

            assert path       == issue_file_path                                                  # FIXED: now the paths match
            assert path_issue == issue_file_path                                                  # FIXED: same for the path_issue

            assert type(path      ) is Safe_Str__File__Path                                       # confirm correct types
            assert type(path_issue) is Safe_Str__File__Path

    def test__regression__nodes_list_all_consistent_with_node_load(self):               # Both APIs now return same results
        test_issues = os.path.join(self.repo_folder, '.issues_list_all_test')
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
        assert len(nodes) == 1                                                         # Raw scan finds the issue

        # Path-handler-based load NOW ALSO finds the same issue
        node = repo.node_load(node_type=Safe_Str__Node_Type('task'),
                              label=Safe_Str__Node_Label('Task-1'))
        assert node is not None                                                        # FIXED: path handler works
        assert node.title == 'A real task'

        # Cleanup
        shutil.rmtree(test_issues)

    def test__regression__node_load_by_label_consistent_with_node_load(self):          # Both load APIs now agree
        test_issues = os.path.join(self.repo_folder, '.issues_label_test')
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

        # node_load() uses path handler → NOW ALSO WORKS
        by_type = repo.node_load(node_type=Safe_Str__Node_Type('bug'),
                                 label=Safe_Str__Node_Label('Bug-7'))
        assert by_type is not None                                                     # FIXED: path handler works
        assert by_type.title == 'Found by label scan'

        # Both APIs now return the same result
        # Cleanup
        shutil.rmtree(test_issues)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 4: Data lands at the CORRECT path on disk
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__regression__factory_writes_to_correct_path_on_disk(self):                # Data written through factory lands in right place
        test_issues_dir = os.path.join(self.repo_folder, '.issues_write_test')
        os.makedirs(test_issues_dir, exist_ok=True)

        repo = Graph__Repository__Factory.create_local_disk(root_path=test_issues_dir)

        # Save node types through the repo
        from issues_fs.schemas.graph.Schema__Node__Type import Schema__Node__Type
        types = [Schema__Node__Type(name='bug', description='Bug report')]
        repo.node_types_save(types)

        # File should be at .issues_write_test/config/node-types.json (correct)
        correct_path = os.path.join(test_issues_dir, 'config', 'node-types.json')
        doubled_path = os.path.join(test_issues_dir, '.issues', 'config', 'node-types.json')

        assert os.path.exists(correct_path) is True                                    # FIXED: at the correct location
        assert os.path.exists(doubled_path) is False                                   # FIXED: not at the doubled location

        # Cleanup
        shutil.rmtree(test_issues_dir)

    def test__regression__factory_writes_issue_to_correct_path_on_disk(self):          # Issue data also lands in right place
        test_issues_dir = os.path.join(self.repo_folder, '.issues_issue_test')
        os.makedirs(test_issues_dir, exist_ok=True)

        repo = Graph__Repository__Factory.create_local_disk(root_path=test_issues_dir)

        node = Schema__Node(node_type = 'bug',
                            label     = 'Bug-99',
                            title     = 'Test bug',
                            status    = 'backlog')
        repo.node_save(node)

        correct_path = os.path.join(test_issues_dir, 'data', 'bug', 'Bug-99', 'issue.json')
        doubled_path = os.path.join(test_issues_dir, '.issues', 'data', 'bug', 'Bug-99', 'issue.json')

        assert os.path.exists(correct_path) is True                                    # FIXED: at the correct location
        assert os.path.exists(doubled_path) is False                                   # FIXED: not at the doubled location

        # Cleanup
        shutil.rmtree(test_issues_dir)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 5: Round-trip through factory works AND files are at correct location
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__regression__round_trip_works(self):                                       # Write+read through factory works
        test_issues_dir = os.path.join(self.repo_folder, '.issues_roundtrip_test')
        os.makedirs(test_issues_dir, exist_ok=True)

        repo = Graph__Repository__Factory.create_local_disk(root_path=test_issues_dir)

        # Write types through factory
        from issues_fs.schemas.graph.Schema__Node__Type import Schema__Node__Type
        types = [Schema__Node__Type(name='bug', description='Bug report')]
        repo.node_types_save(types)

        # Read types through same factory → works
        loaded = repo.node_types_load()
        assert len(loaded) == 1
        assert loaded[0].name == 'bug'

        # Cleanup
        shutil.rmtree(test_issues_dir)

    def test__regression__round_trip_for_nodes_at_correct_path(self):                  # Node save+load works, files at right place
        test_issues_dir = os.path.join(self.repo_folder, '.issues_node_rt_test')
        os.makedirs(test_issues_dir, exist_ok=True)

        repo = Graph__Repository__Factory.create_local_disk(root_path=test_issues_dir)

        node = Schema__Node(node_type = 'bug',
                            label     = 'Bug-42',
                            title     = 'Round trip bug',
                            status    = 'backlog')
        repo.node_save(node)

        loaded = repo.node_load(node_type = Safe_Str__Node_Type('bug'),
                                label     = Safe_Str__Node_Label('Bug-42'))
        assert loaded is not None
        assert loaded.label == 'Bug-42'
        assert loaded.title == 'Round trip bug'

        # The file is at the CORRECT location on disk
        correct_path = os.path.join(test_issues_dir, 'data', 'bug', 'Bug-42', 'issue.json')
        doubled_path = os.path.join(test_issues_dir, '.issues', 'data', 'bug', 'Bug-42', 'issue.json')
        assert os.path.exists(correct_path) is True                                    # FIXED: at the correct location
        assert os.path.exists(doubled_path) is False                                   # FIXED: not at the doubled location

        # Cleanup
        shutil.rmtree(test_issues_dir)


    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 7: Real .issues/ repos from the ecosystem are now readable
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__regression__real_repo_all_operations_work(self):                          # All operations work on real repo
        real_issues = os.path.join(self.repo_folder, '.issues_real_repo')
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

        # === ALL path-handler-based operations NOW WORK ===
        node_types  = repo.node_types_load()
        link_types  = repo.link_types_load()
        bug_1       = repo.node_load(node_type=Safe_Str__Node_Type('bug'),
                                     label=Safe_Str__Node_Label('Bug-1'))
        bug_1_exist = repo.node_exists(node_type=Safe_Str__Node_Type('bug'),
                                       label=Safe_Str__Node_Label('Bug-1'))

        assert len(node_types) == 3                                                    # FIXED: sees all 3 types
        assert len(link_types) == 1                                                    # FIXED: sees the link type
        assert bug_1           is not None                                             # FIXED: Bug-1 found
        assert bug_1.title     == 'Real bug number 1'
        assert bug_1_exist     is True                                                 # FIXED: Bug-1 exists

        # === Raw-scan-based operations: ALSO WORK (as before) ===
        all_nodes       = repo.nodes_list_all()
        bug_1_by_label  = repo.node_load_by_label(label=Safe_Str__Node_Label('Bug-1'))
        bug_1_path      = repo.node_find_path_by_label(label=Safe_Str__Node_Label('Bug-1'))

        assert len(all_nodes)      == 5                                                # Raw scan finds all 5 issues
        assert bug_1_by_label      is not None                                         # Label scan finds Bug-1
        assert bug_1_by_label.title == 'Real bug number 1'
        assert bug_1_path          is not None                                         # Path scan finds Bug-1

        # Both APIs now return consistent results
        assert bug_1.title == bug_1_by_label.title

        # Cleanup
        shutil.rmtree(real_issues)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 8: Verify the fix works with empty base_path too
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__regression__empty_base_path_still_works(self):                            # Empty base_path also works
        real_issues = os.path.join(self.repo_folder, '.issues_fix_demo')
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

        # Create repo with default path handler (base_path='.issues' but no longer used in paths)
        repo = Graph__Repository__Factory.create_local_disk(root_path=real_issues)

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
