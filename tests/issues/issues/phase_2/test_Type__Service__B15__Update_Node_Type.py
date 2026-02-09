# ═══════════════════════════════════════════════════════════════════════════════
# Tests for B15: Config CRUD - Node Types Update Method
# Verifies update_node_type in Type__Service
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                      import Safe_Str__Node_Type, Safe_Str__Status
from issues_fs.schemas.graph.Schema__Node__Type__Update                                                 import Schema__Node__Type__Update
from issues_fs.issues.graph_services.Graph__Repository                                                  import Graph__Repository
from issues_fs.issues.graph_services.Type__Service                                                      import Type__Service
from issues_fs.issues.storage.Path__Handler__Graph_Node                                                 import Path__Handler__Graph_Node


class test_Type__Service__B15__Update_Node_Type(TestCase):

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
    # update_node_type tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__update_node_type__updates_description(self):                      # Test updating description
        updates  = Schema__Node__Type__Update(description = 'Updated description')
        response = self.service.update_node_type(Safe_Str__Node_Type('bug'), updates)

        assert response.success   is True
        assert response.node_type is not None

        reloaded = self.service.get_node_type(Safe_Str__Node_Type('bug'))
        assert str(reloaded.description) == 'Updated description'

    def test__update_node_type__updates_color(self):                            # Test updating color
        updates  = Schema__Node__Type__Update(color = '#00ff00')
        response = self.service.update_node_type(Safe_Str__Node_Type('task'), updates)

        assert response.success is True

        reloaded = self.service.get_node_type(Safe_Str__Node_Type('task'))
        assert str(reloaded.color) == '#00ff00'

    def test__update_node_type__updates_statuses(self):                         # Test updating statuses list
        new_statuses = [Safe_Str__Status('open'), Safe_Str__Status('closed')]
        updates      = Schema__Node__Type__Update(statuses = new_statuses)
        response     = self.service.update_node_type(Safe_Str__Node_Type('feature'), updates)

        assert response.success is True

        reloaded = self.service.get_node_type(Safe_Str__Node_Type('feature'))
        status_strs = [str(s) for s in reloaded.statuses]
        assert 'open'   in status_strs
        assert 'closed' in status_strs

    def test__update_node_type__updates_default_status(self):                   # Test updating default status
        updates  = Schema__Node__Type__Update(default_status = Safe_Str__Status('todo'))
        response = self.service.update_node_type(Safe_Str__Node_Type('task'), updates)

        assert response.success is True

        reloaded = self.service.get_node_type(Safe_Str__Node_Type('task'))
        assert str(reloaded.default_status) == 'todo'

    def test__update_node_type__partial_update(self):                           # Test partial update preserves other fields
        original = self.service.get_node_type(Safe_Str__Node_Type('bug'))
        original_color = str(original.color)

        updates  = Schema__Node__Type__Update(description = 'Only description changed')
        response = self.service.update_node_type(Safe_Str__Node_Type('bug'), updates)

        assert response.success is True

        reloaded = self.service.get_node_type(Safe_Str__Node_Type('bug'))
        assert str(reloaded.description)  == 'Only description changed'
        assert str(reloaded.color)        == original_color                      # Color unchanged

    def test__update_node_type__not_found(self):                                # Test updating nonexistent type
        updates  = Schema__Node__Type__Update(description = 'Does not matter')
        response = self.service.update_node_type(Safe_Str__Node_Type('nonexistent'), updates)

        assert response.success is False
        assert 'not found' in str(response.message)

    def test__update_node_type__response_has_message(self):                     # Test success response message
        updates  = Schema__Node__Type__Update(color = '#ffffff')
        response = self.service.update_node_type(Safe_Str__Node_Type('bug'), updates)

        assert response.success is True
        assert 'updated' in str(response.message).lower()
