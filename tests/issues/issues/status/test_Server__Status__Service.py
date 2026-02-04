# ═══════════════════════════════════════════════════════════════════════════════
# test_Server__Status__Service - Unit tests for main server status orchestrator
# Tests comprehensive status aggregation and health calculation
# ═══════════════════════════════════════════════════════════════════════════════
import sys
from unittest                                                                                               import TestCase
from osbot_utils.testing.__                                                                                 import __, __SKIP__
from memory_fs.helpers.Memory_FS__In_Memory                                                                 import Memory_FS__In_Memory
from mgraph_ai_ui_html_transformation_workbench.schemas.status.Schema__API__Info                            import Schema__API__Info
from mgraph_ai_ui_html_transformation_workbench.schemas.status.Schema__Server__Status                       import Schema__Server__Status
from mgraph_ai_ui_html_transformation_workbench.schemas.status.Schema__Server__Status                       import Schema__Server__Status__Response
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository             import Graph__Repository
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Type__Service                 import Type__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.status.Git__Status__Service                  import Git__Status__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.status.Index__Status__Service                import Index__Status__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.status.Server__Status__Service               import Server__Status__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.status.Storage__Status__Service              import Storage__Status__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.status.Types__Status__Service                import Types__Status__Service
from mgraph_ai_ui_html_transformation_workbench.utils.Version                                               import version__mgraph_ai_service__html_transformation_workbench


# todo: refactor this to use actual services with actual data (i.e. not mocks)
# ═══════════════════════════════════════════════════════════════════════════════
# Mock Sub-Services
# ═══════════════════════════════════════════════════════════════════════════════



class test_Server__Status__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Create mock services
        cls.memory_fs               = Memory_FS__In_Memory()
        cls.storage_fs              = cls.memory_fs.storage_fs
        cls.graph_repository        = Graph__Repository(memory_fs=cls.memory_fs)
        cls.type_service            = Type__Service(repository=cls.graph_repository)

        cls.storage_status__service = Storage__Status__Service(storage_fs=cls.storage_fs)
        cls.git_status__service     = Git__Status__Service    ()
        cls.types_status__service   = Types__Status__Service  (type_service = cls.type_service)
        cls.index_status__service   = Index__Status__Service  (type_service = cls.type_service, repository = cls.graph_repository)

    def setUp(self):                                                             # Reset mocks
        self.storage_status__service.connected   = True
        self.storage_status__service.writable    = True

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test basic initialization
        service = Server__Status__Service()

        assert type(service)            is Server__Status__Service
        assert service.storage_service  is None
        assert service.git_service      is None
        assert service.types_service    is None
        assert service.index_service    is None


    # ═══════════════════════════════════════════════════════════════════════════════
    # get_full_status Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_full_status__returns_response(self):                           # Test return type
        service = Server__Status__Service(storage_service = self.storage_status__service)

        response = service.get_full_status()

        assert type(response) is Schema__Server__Status__Response
        assert response.success is True

    def test__get_full_status__contains_status(self):                            # Test status in response
        service = Server__Status__Service(storage_service = self.storage_status__service)

        response = service.get_full_status()

        assert response.status is not None
        assert type(response.status) is Schema__Server__Status

    def test__get_full_status__has_timestamp(self):                              # Test timestamp present
        service = Server__Status__Service(storage_service = self.storage_status__service)

        response        = service.get_full_status()
        python_version  = sys.version.split()[0]
        assert type(response) is Schema__Server__Status__Response
        assert response.obj() == __(success=True,
                                    status=__(api=__(version=version__mgraph_ai_service__html_transformation_workbench,
                                                     build_date='NA',
                                                     environment='development',
                                                     python_version=python_version,
                                                     api_name='Graph Issue Tracking API'),
                                              storage=__(backend_type='Storage_FS__Memory',
                                                         root_path='',
                                                         is_connected=True,
                                                         is_writable=True,
                                                         file_count=0),
                                              types=None,
                                              index=None,
                                              git=None,
                                              timestamp=__SKIP__),
                                    message='')


    def test__get_full_status__all_components(self):                             # Test all components present
        service = Server__Status__Service(storage_service = self.storage_status__service,
                                          git_service     = self.git_status__service,
                                          types_service   = self.types_status__service,
                                          index_service   = self.index_status__service)

        response = service.get_full_status()
        status   = response.status

        assert response.message == ''
        assert response.success is True
        assert status.api       is not None
        assert status.storage   is not None
        assert status.git       is not None
        assert status.types     is not None
        assert status.index     is not None

    def test__get_full_status__missing_services(self):                           # Test with missing services
        service = Server__Status__Service()                                      # No services configured

        response = service.get_full_status()

        assert response.success is True
        assert response.status.api is not None                                   # API info always available

    # ═══════════════════════════════════════════════════════════════════════════════
    # API Info Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_api_info(self):                                                # Test API info getter
        service = Server__Status__Service()

        api_info = service.get_api_info()

        assert type(api_info) is Schema__API__Info
        assert str(api_info.version)        != ''
        assert str(api_info.api_name)       != ''
        assert str(api_info.python_version) != ''

    def test__get_api_info__version_format(self):                                # Test version format
        service = Server__Status__Service()

        api_info = service.get_api_info()

        version = str(api_info.version)
        assert '.' in version                                                    # Semantic versioning


