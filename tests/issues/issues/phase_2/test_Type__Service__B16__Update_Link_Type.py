# ═══════════════════════════════════════════════════════════════════════════════
# Tests for B16: Config CRUD - Link Types Update Method
# Verifies update_link_type in Type__Service
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                      import Safe_Str__Link_Verb, Safe_Str__Node_Type
from issues_fs.schemas.graph.Schema__Link__Type__Update                                                 import Schema__Link__Type__Update
from issues_fs.issues.graph_services.Graph__Repository                                                  import Graph__Repository
from issues_fs.issues.graph_services.Type__Service                                                      import Type__Service
from issues_fs.issues.storage.Path__Handler__Graph_Node                                                 import Path__Handler__Graph_Node


class test_Type__Service__B16__Update_Link_Type(TestCase):

    @classmethod
    def setUpClass(cls):                                                        # Shared setup for all tests
        cls.memory_fs    = Memory_FS__In_Memory()
        cls.path_handler = Path__Handler__Graph_Node()
        cls.repository   = Graph__Repository(memory_fs    = cls.memory_fs   ,
                                              path_handler = cls.path_handler)
        cls.service      = Type__Service(repository=cls.repository)
        cls.service.initialize_default_types()

    def setUp(self):                                                            # Reset storage before each test
        self.repository.clear_storage()
        self.service.initialize_default_types()

    # ═══════════════════════════════════════════════════════════════════════════════
    # update_link_type tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__update_link_type__updates_description(self):                      # Test updating description
        updates  = Schema__Link__Type__Update(description = 'Updated blocking description')
        response = self.service.update_link_type(Safe_Str__Link_Verb('blocks'), updates)

        assert response.success   is True
        assert response.link_type is not None

        reloaded = self.service.get_link_type(Safe_Str__Link_Verb('blocks'))
        assert str(reloaded.description) == 'Updated blocking description'

    def test__update_link_type__updates_inverse_verb(self):                     # Test updating inverse verb
        updates  = Schema__Link__Type__Update(inverse_verb = Safe_Str__Link_Verb('is-blocked-by'))
        response = self.service.update_link_type(Safe_Str__Link_Verb('blocks'), updates)

        assert response.success is True

        reloaded = self.service.get_link_type(Safe_Str__Link_Verb('blocks'))
        assert str(reloaded.inverse_verb) == 'is-blocked-by'

    def test__update_link_type__updates_source_types(self):                     # Test updating source types
        new_source_types = [Safe_Str__Node_Type('bug'), Safe_Str__Node_Type('task'), Safe_Str__Node_Type('feature')]
        updates          = Schema__Link__Type__Update(source_types = new_source_types)
        response         = self.service.update_link_type(Safe_Str__Link_Verb('blocks'), updates)

        assert response.success is True

        reloaded    = self.service.get_link_type(Safe_Str__Link_Verb('blocks'))
        source_strs = [str(s) for s in reloaded.source_types]
        assert 'feature' in source_strs
        assert len(source_strs) == 3

    def test__update_link_type__updates_target_types(self):                     # Test updating target types
        new_target_types = [Safe_Str__Node_Type('task')]
        updates          = Schema__Link__Type__Update(target_types = new_target_types)
        response         = self.service.update_link_type(Safe_Str__Link_Verb('has-task'), updates)

        assert response.success is True

        reloaded    = self.service.get_link_type(Safe_Str__Link_Verb('has-task'))
        target_strs = [str(t) for t in reloaded.target_types]
        assert target_strs == ['task']

    def test__update_link_type__partial_update(self):                           # Test partial update preserves other fields
        original = self.service.get_link_type(Safe_Str__Link_Verb('blocks'))
        original_inverse = str(original.inverse_verb)

        updates  = Schema__Link__Type__Update(description = 'Only description changed')
        response = self.service.update_link_type(Safe_Str__Link_Verb('blocks'), updates)

        assert response.success is True

        reloaded = self.service.get_link_type(Safe_Str__Link_Verb('blocks'))
        assert str(reloaded.description)  == 'Only description changed'
        assert str(reloaded.inverse_verb) == original_inverse                    # Inverse unchanged

    def test__update_link_type__not_found(self):                                # Test updating nonexistent type
        updates  = Schema__Link__Type__Update(description = 'Does not matter')
        response = self.service.update_link_type(Safe_Str__Link_Verb('nonexistent'), updates)

        assert response.success is False
        assert 'not found' in str(response.message)

    def test__update_link_type__response_has_message(self):                     # Test success response message
        updates  = Schema__Link__Type__Update(description = 'New desc')
        response = self.service.update_link_type(Safe_Str__Link_Verb('blocks'), updates)

        assert response.success is True
        assert 'updated' in str(response.message).lower()
