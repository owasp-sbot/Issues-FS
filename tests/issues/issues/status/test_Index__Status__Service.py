# ═══════════════════════════════════════════════════════════════════════════════
# test_Index__Status__Service - Unit tests for index and node statistics
# Tests global index and per-type node count reporting
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                               import TestCase

from osbot_utils.testing.__ import __, __SKIP__
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                        import Safe_UInt
from memory_fs.helpers.Memory_FS__In_Memory                                                                 import Memory_FS__In_Memory
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types import Safe_Str__Node_Label
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Link__Create__Request import Schema__Link__Create__Request
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Create__Request import Schema__Node__Create__Request
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Create__Response import Schema__Node__Create__Response
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Type                            import Schema__Node__Type
from mgraph_ai_ui_html_transformation_workbench.schemas.status.Schema__Index__Status                        import Schema__Index__Status
from mgraph_ai_ui_html_transformation_workbench.schemas.status.Schema__Index__Status                        import Schema__Type__Count
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository             import Graph__Repository
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Link__Service import Link__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Node__Service import Node__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Type__Service                 import Type__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.status.Index__Status__Service                import Index__Status__Service




class test_Index__Status__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared test data

        cls.memory_fs               = Memory_FS__In_Memory()
        cls.storage_fs              = cls.memory_fs.storage_fs
        cls.graph_repository        = Graph__Repository(memory_fs=cls.memory_fs)
        cls.link_service            = Link__Service(repository=cls.graph_repository)
        cls.node_service            = Node__Service(repository=cls.graph_repository)
        cls.type_service            = Type__Service(repository=cls.graph_repository)

        #cls.storage_status__service = Storage__Status__Service(storage_fs=cls.storage_fs)
        #cls.git_status__service     = Git__Status__Service    ()
        #cls.types_status__service   = Types__Status__Service  (type_service = cls.type_service)
        cls.index_status__service   = Index__Status__Service  (type_service = cls.type_service, repository = cls.graph_repository)

        cls.create_test_data()

    @classmethod
    def create_test_data(cls):
        cls.bug_type = cls.type_service.create_node_type(name         = 'bug'      ,
                                                         display_name = 'Bug'      ,
                                                         color        = '#ef4444'  ,
                                                         statuses     = ['backlog', 'confirmed', 'resolved'])

        cls.task_type = cls.type_service.create_node_type(name         = 'task'    ,
                                                          display_name = 'Task'    ,
                                                          color        = '#3b82f6' ,
                                                          statuses     = ['todo', 'in-progress', 'done'])

        cls.blocks_link = cls.type_service.create_link_type(verb         = 'blocks'    ,
                                                            inverse_verb = 'blocked-by',
                                                            source_types = ['bug'],
                                                            target_types = ['bug'])

        cls.relates_link = cls.type_service.create_link_type(verb         = 'relates-to',
                                                             inverse_verb = 'relates-to')

        cls.bug_type  = Schema__Node__Type(name='bug')
        cls.task_type = Schema__Node__Type(name='task')

        cls.bug_index  = Schema__Type__Count(count=15, next_index=16)
        cls.task_index = Schema__Type__Count(count=27, next_index=28)

        cls.bug_node__request = Schema__Node__Create__Request(node_type = 'bug',
                                                              title     =  'an bug')
        cls.bug_node          = cls.node_service.create_node(request =cls.bug_node__request)
        assert type(cls.bug_node) is Schema__Node__Create__Response
        assert cls.bug_node.obj() == __(success=True,
                                        node=__(node_id=__SKIP__,
                                                node_type='bug',
                                                node_index=1,
                                                label='Bug-1',
                                                title='an bug',
                                                description='',
                                                status='backlog',
                                                created_at=__SKIP__,
                                                updated_at=__SKIP__,
                                                created_by=__SKIP__,
                                                tags=[],
                                                links=[],
                                                properties=__()),
                                        message='')

        cls.bug_link_request = Schema__Link__Create__Request(verb='blocks',
                                                             target_label = 'Bug-1')
        cls.bug_link = cls.link_service.create_link(source_type  = 'bug',
                                                    source_label = Safe_Str__Node_Label('Bug-1'),
                                                    request      = cls.bug_link_request)

        assert cls.bug_link.obj() == __(success=True,
                                        source_link=__(link_type_id=__SKIP__,
                                                       verb='blocks',
                                                       target_id=__SKIP__,
                                                       target_label='Bug-1',
                                                       created_at=__SKIP__),
                                        target_link=__(link_type_id=__SKIP__,
                                                       verb='blocked-by',
                                                       target_id=__SKIP__,
                                                       target_label='Bug-1',
                                                       created_at=__SKIP__),
                                        message='')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test service initialization
        service = Index__Status__Service()

        assert type(service)        is Index__Status__Service
        assert service.repository   is None
        assert service.type_service is None


    # ═══════════════════════════════════════════════════════════════════════════════
    # get_status Tests
    # ═══════════════════════════════════════════════════════════════════════════════


    def test__get_status(self):                               # Test with global index

        status = self.index_status__service.get_status()

        assert status.global_index_exists is True
        assert status.obj()               == __(global_index_exists=True,
                                                total_nodes=1,
                                                #total_links=0,
                                                last_updated=__SKIP__,
                                                type_counts=[__(node_type='bug', count=1, next_index=2),
                                                             __(node_type='task', count=0, next_index=1)])



    # ═══════════════════════════════════════════════════════════════════════════════
    # _check_global_index_exists Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___check_global_index_exists__true(self):                            # Test exists
        result = self.index_status__service._check_global_index_exists()

        assert result is True



    # ═══════════════════════════════════════════════════════════════════════════════
    # _get_count_for_type Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___get_count_for_type__exists(self):                                 # Test type exists
        result = self.index_status__service._get_count_for_type('bug')

        assert result == 1

    def test___get_count_for_type__not_exists(self):                             # Test type not exists
        result = self.index_status__service._get_count_for_type('unknown')

        assert result == 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # _get_next_index_for_type Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___get_next_index_for_type__exists(self):                            # Test type exists
        result = self.index_status__service._get_next_index_for_type('bug')

        assert result == 2

    def test___get_next_index_for_type__not_exists(self):                        # Test type not exists
        result = self.index_status__service._get_next_index_for_type('unknown')

        assert result == 1                                                       # Default is 1

    # ═══════════════════════════════════════════════════════════════════════════════
    # _calculate_total_nodes Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___calculate_total_nodes__empty(self):                               # Test empty list
        service = Index__Status__Service()

        result = service._calculate_total_nodes([])

        assert result == 0

    def test___calculate_total_nodes__multiple(self):                            # Test multiple counts
        status = self.index_status__service.get_status()
        counts = status.type_counts

        result = self.index_status__service._calculate_total_nodes(counts)      # todo: review the need to pass this counts var here

        assert result == 1
