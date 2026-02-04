# ═══════════════════════════════════════════════════════════════════════════════
# test_Type__Service__Phase1 - Tests for Phase 1 git-repo type addition
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from issues_fs.issues.graph_services.Graph__Repository         import Graph__Repository
from issues_fs.issues.graph_services.Type__Service             import Type__Service
from issues_fs.issues.storage.Path__Handler__Graph_Node        import Path__Handler__Graph_Node


class test_Type__Service__Phase_1(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup for all tests
        cls.memory_fs    = Memory_FS__In_Memory()
        cls.path_handler = Path__Handler__Graph_Node()
        cls.repository   = Graph__Repository(memory_fs    = cls.memory_fs   ,
                                             path_handler = cls.path_handler)
        cls.type_service = Type__Service(repository = cls.repository)

    def setUp(self):                                                             # Reset storage before each test
        self.repository.clear_storage()

    # ═══════════════════════════════════════════════════════════════════════════════
    # B0: git-repo Type Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__initialize_default_types__creates_git_repo(self):                  # Test git-repo type is created
        self.type_service.initialize_default_types()

        git_repo_type = self.type_service.get_node_type('git-repo')

        assert git_repo_type                    is not None
        assert str(git_repo_type.name)          == 'git-repo'
        assert str(git_repo_type.display_name)  == 'GitRepo'
        assert str(git_repo_type.color)         == '#6366f1'
        assert 'active'                         in git_repo_type.statuses
        assert 'archived'                       in git_repo_type.statuses
        assert str(git_repo_type.default_status) == 'active'

    def test__initialize_default_types__git_repo_first(self):                    # Test git-repo is first type
        self.type_service.initialize_default_types()

        node_types = self.type_service.list_node_types()

        assert len(node_types)          >= 5                                     # At least 5 types
        assert str(node_types[0].name)  == 'git-repo'                           # git-repo should be first

    def test__initialize_default_types__all_types_exist(self):                   # Test all default types created
        self.type_service.initialize_default_types()

        expected_types = ['git-repo', 'bug', 'task', 'feature', 'person']
        node_types     = self.type_service.list_node_types()
        type_names     = [str(t.name) for t in node_types]

        for expected in expected_types:
            assert expected in type_names

    def test__initialize_default_types__contains_link_type(self):                # Test contains link type created
        self.type_service.initialize_default_types()

        contains_type = self.type_service.get_link_type('contains')

        assert contains_type                    is not None
        assert str(contains_type.verb)          == 'contains'
        assert str(contains_type.inverse_verb)  == 'contained-by'
        assert 'git-repo'                       in [str(t) for t in contains_type.source_types]

    def test__initialize_default_types__idempotent(self):                        # Test double init doesn't duplicate
        self.type_service.initialize_default_types()
        count_first = len(self.type_service.list_node_types())

        self.type_service.initialize_default_types()                             # Call again
        count_second = len(self.type_service.list_node_types())

        assert count_first == count_second                                       # Should not create duplicates

    def test__has_task_link__includes_git_repo(self):                            # Test has-task allows git-repo source
        self.type_service.initialize_default_types()

        has_task_type = self.type_service.get_link_type('has-task')

        assert has_task_type is not None
        source_types = [str(t) for t in has_task_type.source_types]
        assert 'git-repo' in source_types                                        # git-repo can have tasks
        assert 'feature'  in source_types

    def test__relates_to_link__includes_git_repo(self):                          # Test relates-to allows git-repo
        self.type_service.initialize_default_types()

        relates_type = self.type_service.get_link_type('relates-to')

        assert relates_type is not None
        source_types = [str(t) for t in relates_type.source_types]
        target_types = [str(t) for t in relates_type.target_types]
        assert 'git-repo' in source_types
        assert 'git-repo' in target_types
