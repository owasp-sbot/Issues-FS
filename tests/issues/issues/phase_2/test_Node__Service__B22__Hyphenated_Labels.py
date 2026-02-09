# ═══════════════════════════════════════════════════════════════════════════════
# Tests for B22: Hyphenated Label Support
# Verifies label_from_type_and_index, type_to_label_prefix, parse_label_to_type,
# and updated resolve_link_target
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                        import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                        import Timestamp_Now
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                      import Safe_Str__Node_Type, Safe_Str__Node_Label
from issues_fs.schemas.graph.Schema__Node                                                               import Schema__Node
from issues_fs.schemas.graph.Schema__Node__Link                                                         import Schema__Node__Link
from issues_fs.issues.graph_services.Graph__Repository                                                  import Graph__Repository
from issues_fs.issues.graph_services.Node__Service                                                      import Node__Service
from issues_fs.issues.graph_services.Type__Service                                                      import Type__Service
from issues_fs.issues.storage.Path__Handler__Graph_Node                                                 import Path__Handler__Graph_Node


class test_Node__Service__B22__Hyphenated_Labels(TestCase):

    @classmethod
    def setUpClass(cls):                                                        # Shared setup for all tests
        cls.memory_fs    = Memory_FS__In_Memory()
        cls.path_handler = Path__Handler__Graph_Node()
        cls.repository   = Graph__Repository(memory_fs    = cls.memory_fs   ,
                                              path_handler = cls.path_handler)
        cls.service      = Node__Service(repository=cls.repository)
        cls.type_service = Type__Service(repository=cls.repository)
        cls.type_service.initialize_default_types()

    def setUp(self):                                                            # Reset storage before each test
        self.repository.clear_storage()
        self.type_service.initialize_default_types()                            # Re-initialize after clear

    # ═══════════════════════════════════════════════════════════════════════════════
    # label_from_type_and_index tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__label_from_type_and_index__single_word(self):                     # Test single-word type
        result = self.service.label_from_type_and_index(Safe_Str__Node_Type('task'), 1)
        assert str(result) == 'Task-1'

    def test__label_from_type_and_index__single_word_bug(self):                 # Test bug type
        result = self.service.label_from_type_and_index(Safe_Str__Node_Type('bug'), 5)
        assert str(result) == 'Bug-5'

    def test__label_from_type_and_index__hyphenated_type(self):                 # Test hyphenated type
        result = self.service.label_from_type_and_index(Safe_Str__Node_Type('git-repo'), 1)
        assert str(result) == 'Git-Repo-1'

    def test__label_from_type_and_index__multi_hyphenated(self):                # Test multi-word hyphenated type
        self.type_service.create_node_type(name         = Safe_Str__Node_Type('user-story'),
                                            display_name = 'User Story'                    ,
                                            description  = 'User story'                    )
        result = self.service.label_from_type_and_index(Safe_Str__Node_Type('user-story'), 5)
        assert str(result) == 'User-Story-5'

    # ═══════════════════════════════════════════════════════════════════════════════
    # type_to_label_prefix tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__type_to_label_prefix__single_word(self):                          # Test single word
        result = self.service.type_to_label_prefix('task')
        assert result == 'Task'

    def test__type_to_label_prefix__hyphenated(self):                           # Test hyphenated
        result = self.service.type_to_label_prefix('git-repo')
        assert result == 'Git-Repo'

    def test__type_to_label_prefix__multi_hyphenated(self):                     # Test multi-hyphenated
        result = self.service.type_to_label_prefix('user-story')
        assert result == 'User-Story'

    # ═══════════════════════════════════════════════════════════════════════════════
    # parse_label_to_type tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__parse_label_to_type__single_word(self):                           # Test parsing single-word label
        result = self.service.parse_label_to_type(Safe_Str__Node_Label('Task-1'))
        assert str(result) == 'task'

    def test__parse_label_to_type__bug(self):                                   # Test parsing bug label
        result = self.service.parse_label_to_type(Safe_Str__Node_Label('Bug-5'))
        assert str(result) == 'bug'

    def test__parse_label_to_type__hyphenated_known_type(self):                 # Test parsing known hyphenated type
        result = self.service.parse_label_to_type(Safe_Str__Node_Label('Git-Repo-1'))
        assert str(result) == 'git-repo'

    def test__parse_label_to_type__multi_word_known_type(self):                 # Test parsing multi-word known type
        self.type_service.create_node_type(name         = Safe_Str__Node_Type('user-story'),
                                            display_name = 'User Story'                    ,
                                            description  = 'User story'                    )
        result = self.service.parse_label_to_type(Safe_Str__Node_Label('User-Story-5'))
        assert str(result) == 'user-story'

    def test__parse_label_to_type__fallback(self):                              # Test fallback for unknown type
        result = self.service.parse_label_to_type(Safe_Str__Node_Label('Unknown-42'))
        assert str(result) == 'unknown'

    # ═══════════════════════════════════════════════════════════════════════════════
    # resolve_link_target tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__resolve_link_target__single_word_type(self):                      # Test resolving single-word type
        now  = Timestamp_Now()
        node = Schema__Node(node_id    = Obj_Id()                         ,
                             node_type  = Safe_Str__Node_Type('bug')      ,
                             label      = Safe_Str__Node_Label('Bug-1')   ,
                             title      = 'Test Bug'                      ,
                             created_at = now                              ,
                             updated_at = now                              ,
                             created_by = Obj_Id()                         )
        self.repository.node_save(node)

        link = Schema__Node__Link(target_label = Safe_Str__Node_Label('Bug-1'),
                                   verb         = 'blocks'                     )
        result = self.service.resolve_link_target(link)
        assert result            is not None
        assert str(result.label) == 'Bug-1'

    def test__resolve_link_target__hyphenated_type(self):                       # Test resolving hyphenated type
        now  = Timestamp_Now()
        node = Schema__Node(node_id    = Obj_Id()                             ,
                             node_type  = Safe_Str__Node_Type('git-repo')     ,
                             label      = Safe_Str__Node_Label('Git-Repo-1')  ,
                             title      = 'Test Repo'                         ,
                             created_at = now                                  ,
                             updated_at = now                                  ,
                             created_by = Obj_Id()                             )
        self.repository.node_save(node)

        link = Schema__Node__Link(target_label = Safe_Str__Node_Label('Git-Repo-1'),
                                   verb         = 'relates-to'                      )
        result = self.service.resolve_link_target(link)
        assert result            is not None
        assert str(result.label) == 'Git-Repo-1'

    def test__resolve_link_target__empty_label(self):                           # Test with empty target label
        link = Schema__Node__Link(verb = 'blocks')
        result = self.service.resolve_link_target(link)
        assert result is None

    def test__resolve_link_target__nonexistent_node(self):                      # Test with non-existent target
        link = Schema__Node__Link(target_label = Safe_Str__Node_Label('Bug-999'),
                                   verb         = 'blocks'                       )
        result = self.service.resolve_link_target(link)
        assert result is None
