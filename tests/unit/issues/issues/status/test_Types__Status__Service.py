# ═══════════════════════════════════════════════════════════════════════════════
# test_Types__Status__Service - Unit tests for type configuration status
# Tests node type and link type status reporting
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                   import TestCase
from osbot_utils.testing.__                                                                     import __
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                           import Type_Safe__List
from memory_fs.helpers.Memory_FS__In_Memory                                                     import Memory_FS__In_Memory
from issues_fs.schemas.status.Schema__Types__Status            import Schema__Types__Status
from issues_fs.issues.graph_services.Graph__Repository import Graph__Repository
from issues_fs.issues.graph_services.Type__Service     import Type__Service
from issues_fs.issues.status.Types__Status__Service    import Types__Status__Service

class test_Types__Status__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared test data
        cls.memory_fs            = Memory_FS__In_Memory()
        cls.graph_repository     = Graph__Repository(memory_fs=cls.memory_fs)
        cls.type_service         = Type__Service(repository=cls.graph_repository)
        cls.types_status_service = Types__Status__Service(type_service = cls.type_service)

        cls.bug_type = cls.type_service.create_node_type(name         = 'bug'      ,
                                                         display_name = 'Bug'      ,
                                                         color        = '#ef4444'  ,
                                                         statuses     = ['backlog', 'confirmed', 'resolved'])

        cls.task_type = cls.type_service.create_node_type(name         = 'task'    ,
                                                          display_name = 'Task'    ,
                                                          color        = '#3b82f6' ,
                                                          statuses     = ['todo', 'in-progress', 'done'])

        cls.blocks_link = cls.type_service.create_link_type(verb         = 'blocks'    ,
                                                            inverse_verb = 'blocked-by')

        cls.relates_link = cls.type_service.create_link_type(verb         = 'relates-to',
                                                             inverse_verb = 'relates-to')


    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test service initialization
        service = Types__Status__Service()

        assert type(service)        is Types__Status__Service
        assert service.type_service is None


    # ═══════════════════════════════════════════════════════════════════════════════
    # get_status Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_status__no_type_service(self):                                 # Test without type service
        service = Types__Status__Service()

        status = service.get_status()

        assert type(status)           is Schema__Types__Status
        assert status.is_initialized  is False
        assert len(status.node_types) == 0
        assert len(status.link_types) == 0

    def test__get_status(self):
        with self.types_status_service as _:
            status = _.get_status()

            assert status.is_initialized       is True
            assert int(status.node_type_count) == 2
            assert int(status.link_type_count) == 2


    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Type Summary Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___get_node_type_summaries__returns_list(self):                      # Test summary list
        with self.types_status_service as _:
            summaries = _._get_node_type_summaries()

            assert type(summaries) is Type_Safe__List
            assert len(summaries)  == 2
            assert summaries.obj() == [__(name='bug' , display_name='Bug' , color='#ef4444', status_count=3),
                                       __(name='task', display_name='Task', color='#3b82f6', status_count=3)]


    # ═══════════════════════════════════════════════════════════════════════════════
    # Link Type Summary Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___get_link_type_summaries__returns_list(self):                      # Test link summary list
        with self.types_status_service as _:
            summaries = _._get_link_type_summaries()

            assert type(summaries) is Type_Safe__List
            assert len(summaries)  == 2
            assert summaries.obj() == [__(verb='blocks'    , inverse_verb='blocked-by', is_symmetric=False),
                                       __(verb='relates-to', inverse_verb='relates-to', is_symmetric=True)]
