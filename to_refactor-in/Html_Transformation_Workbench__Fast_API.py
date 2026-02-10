# ═══════════════════════════════════════════════════════════════════════════════
# Html_Transformation_Workbench__Fast_API - Main FastAPI application
# Phase 1: Added root selection service and routes
# Phase 2: Added MGraphDB sync service and graph routes
# ═══════════════════════════════════════════════════════════════════════════════

import mgraph_ai_ui_html_transformation_workbench__ui
from fastapi                                                                                     import Response
from osbot_utils.utils.Env                                                                       import get_env
from osbot_utils.utils.Files                                                                     import path_combine, file_contents
from memory_fs.Memory_FS                                                                         import Memory_FS
from mgraph_ai_ui_html_transformation_workbench.fast_api.routes.Routes__Comments                 import Routes__Comments
from mgraph_ai_ui_html_transformation_workbench.fast_api.routes.Routes__Graph                    import Routes__Graph
from mgraph_ai_ui_html_transformation_workbench.fast_api.routes.phase_1.Routes__Roots            import Routes__Roots
from mgraph_ai_ui_html_transformation_workbench.fast_api.routes.phase_1.Routes__Issues           import Routes__Issues
from mgraph_ai_ui_html_transformation_workbench.schemas.issues.phase_1.Schema__Root              import Schema__Root__Select__Request
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Comments__Service  import Comments__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.phase_1.Issue__Children__Service  import Issue__Children__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.phase_1.Root__Issue__Service      import Root__Issue__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.phase_1.Root__Selection__Service  import Root__Selection__Service
from mgraph_ai_ui_html_transformation_workbench.services.mgraph.MGraph__Issues__Sync__Service    import MGraph__Issues__Sync__Service
from osbot_fast_api_serverless.fast_api.routes.Routes__Info                                      import Routes__Info
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                import Safe_Str__File__Path
from memory_fs.storage_fs.providers.Storage_FS__Local_Disk                                       import Storage_FS__Local_Disk
from memory_fs.storage_fs.providers.Storage_FS__Memory                                           import Storage_FS__Memory
from mgraph_ai_ui_html_transformation_workbench.fast_api.routes.Routes__Links                    import Routes__Links
from mgraph_ai_ui_html_transformation_workbench.fast_api.routes.Routes__Nodes                    import Routes__Nodes
from mgraph_ai_ui_html_transformation_workbench.fast_api.routes.Routes__Server                   import Routes__Server
from mgraph_ai_ui_html_transformation_workbench.fast_api.routes.Routes__Types                    import Routes__Types
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository  import Graph__Repository
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Link__Service      import Link__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Node__Service      import Node__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Type__Service      import Type__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.status.Git__Status__Service       import Git__Status__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.status.Index__Status__Service     import Index__Status__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.status.Server__Status__Service    import Server__Status__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.status.Storage__Status__Service   import Storage__Status__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.status.Types__Status__Service     import Types__Status__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.storage.Path__Handler__Graph_Node import Path__Handler__Graph_Node
from osbot_fast_api.api.routes.Routes__Set_Cookie                                                import Routes__Set_Cookie
from starlette.responses                                                                         import RedirectResponse
from starlette.staticfiles                                                                       import StaticFiles
from osbot_fast_api.api.decorators.route_path                                                    import route_path
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API                                     import Serverless__Fast_API
from mgraph_ai_ui_html_transformation_workbench.config                                           import UI__CONSOLE__ROUTE__CONSOLE, FAST_API__TITLE, FAST_API__DESCRIPTION, UI__CONSOLE__MAJOR__VERSION, UI__CONSOLE__LATEST__VERSION, UI__CONSOLE__ROUTE__START_PAGE
from mgraph_ai_ui_html_transformation_workbench.utils.Version                                    import version__mgraph_ai_service__html_transformation_workbench

ROUTES_PATHS__CONSOLE = [f'/{UI__CONSOLE__ROUTE__CONSOLE}',
                         '/events/server']

# ═══════════════════════════════════════════════════════════════════════════════
# Environment Variable Names
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT__ISSUES_PATH       = '.issues'
ENV_VAR__ISSUES__IN_MEMORY = 'ISSUES__IN_MEMORY'                                 # Set to 'false' to use local disk
ENV_VAR__ISSUES__PATH      = 'ISSUES__PATH'                                      # Path to .issues folder
ENV_VAR__ISSUES__ROOT_PATH = 'ISSUES__ROOT_PATH'                                 # Default root path within issues


class Html_Transformation_Workbench__Fast_API(Serverless__Fast_API):
    run_in_memory   : bool                 = True
    issues_path     : Safe_Str__File__Path = DEFAULT__ISSUES_PATH
    root_path       : Safe_Str__File__Path = ''                                  # Root path within issues
    memory_fs       : Memory_FS            = None
    path_handler    : Path__Handler__Graph_Node = None                           # Shared path handler

    # Core services
    graph_repository      : Graph__Repository    = None
    link_service          : Link__Service        = None
    node_service          : Node__Service        = None
    type_service          : Type__Service        = None
    comments_service      : Comments__Service    = None

    # Phase 1: Root selection services
    root_selection_service  : Root__Selection__Service  = None
    root_issue_service      : Root__Issue__Service      = None
    issue_children_service  : Issue__Children__Service  = None

    # Phase 2: MGraphDB services
    mgraph_sync_service     : MGraph__Issues__Sync__Service = None

    # Status services
    storage_status__service : Storage__Status__Service = None
    git_status__service     : Git__Status__Service     = None
    types_status__service   : Types__Status__Service   = None
    index_status__service   : Index__Status__Service   = None
    server_status_service   : Server__Status__Service  = None

    def setup(self):
        with self.config as _:
            _.name           = FAST_API__TITLE
            _.version        = version__mgraph_ai_service__html_transformation_workbench
            _.description    = FAST_API__DESCRIPTION

            self.setup_services()

        return super().setup()

    def setup_routes(self):
        self.add_routes(Routes__Links   , service = self.link_service          )
        self.add_routes(Routes__Nodes   , service = self.node_service          )
        self.add_routes(Routes__Types   , service = self.type_service          )
        self.add_routes(Routes__Server  , service = self.server_status_service )
        self.add_routes(Routes__Comments, service = self.comments_service      )
        self.add_routes(Routes__Roots   , service = self.root_selection_service)
        self.add_routes(Routes__Issues  , service = self.issue_children_service)
        self.add_routes(Routes__Graph   , sync_service = self.mgraph_sync_service)  # Phase 2

        self.add_routes(Routes__Info)
        self.add_routes(Routes__Set_Cookie)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Service Setup
    # ═══════════════════════════════════════════════════════════════════════════════

    def setup_services(self):                                                    # Initialize the service dependency chain
        use_memory  = self.resolve_storage_mode()
        issues_path = self.resolve_issues_path()
        root_path   = self.resolve_root_path()

        if use_memory:
            storage_fs      = Storage_FS__Memory()
            path_base       = issues_path                                        # Memory storage needs full path prefix
        else:
            self.run_in_memory = False
            storage_fs      = Storage_FS__Local_Disk(root_path=issues_path)
            path_base       = ''                                                 # Local disk storage already rooted at issues_path

        self.memory_fs    = Memory_FS(storage_fs=storage_fs)
        self.path_handler = Path__Handler__Graph_Node(base_path=path_base)

        self.graph_repository = Graph__Repository(memory_fs    = self.memory_fs   ,
                                                  path_handler = self.path_handler)

        # Phase 1: Root selection services (must be created before Node__Service)
        self.root_selection_service = Root__Selection__Service(repository   = self.graph_repository,
                                                               path_handler = self.path_handler    )
        self.root_issue_service     = Root__Issue__Service    (repository   = self.graph_repository,
                                                               path_handler = self.path_handler    )
        self.issue_children_service = Issue__Children__Service(repository   = self.graph_repository,
                                                               path_handler = self.path_handler    )

        # Core services - Phase 2: Node service needs root selection
        self.type_service     = Type__Service    (repository = self.graph_repository)
        self.node_service     = Node__Service    (repository             = self.graph_repository      ,
                                                  root_selection_service = self.root_selection_service)
        self.link_service     = Link__Service    (repository = self.graph_repository)
        self.comments_service = Comments__Service(repository = self.graph_repository)

        # Phase 2: MGraphDB sync service
        self.mgraph_sync_service = MGraph__Issues__Sync__Service(
            repository   = self.graph_repository,
            path_handler = self.path_handler    )

        # Status services
        self.storage_status__service = Storage__Status__Service(storage_fs   = storage_fs)
        self.git_status__service     = Git__Status__Service    ()
        self.types_status__service   = Types__Status__Service  (type_service = self.type_service  )
        self.index_status__service   = Index__Status__Service  (type_service = self.type_service  ,
                                                                repository   = self.graph_repository)
        self.server_status_service   = Server__Status__Service(storage_service = self.storage_status__service,
                                                               git_service     = self.git_status__service    ,
                                                               types_service   = self.types_status__service  ,
                                                               index_service   = self.index_status__service  )

        # Initialize defaults
        self.type_service.initialize_default_types()
        self.root_issue_service.ensure_root_issue_exists()                       # Phase 1: Create root GitRepo-1

        # Apply configured root if set
        if root_path:
            self.root_selection_service.set_current_root(Schema__Root__Select__Request(path=root_path))

        self.root_path = root_path

    # ═══════════════════════════════════════════════════════════════════════════════
    # Configuration Resolution
    # ═══════════════════════════════════════════════════════════════════════════════

    def resolve_storage_mode(self) -> bool:
        env_value = get_env(ENV_VAR__ISSUES__IN_MEMORY, None)

        if env_value is not None:
            return env_value.lower() not in ('false', '0', 'no', 'off')

        return self.run_in_memory

    def resolve_issues_path(self) -> str:
        env_value = get_env(ENV_VAR__ISSUES__PATH, None)

        if env_value:
            return env_value

        return str(self.issues_path)

    def resolve_root_path(self) -> str:
        env_value = get_env(ENV_VAR__ISSUES__ROOT_PATH, None)

        if env_value:
            return env_value

        if self.root_path:
            return str(self.root_path)

        return ''

    def get_current_root_path(self) -> str:
        if self.root_path:
            return self.root_path
        return str(self.issues_path)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Static Routes
    # ═══════════════════════════════════════════════════════════════════════════════

    def add_chrome_llm_routes(self):
        def get_file(file_path):
            root_path = mgraph_ai_ui_html_transformation_workbench__ui.path
            js_path = path_combine(root_path, file_path)

            return Response(file_contents(js_path), media_type='text/javascript')

        @route_path('/service-worker.js')
        def service_worker_js():
            return get_file('chrome-llm/src/service-worker.js')


        @route_path('/workbench/chrome-llm/manifest.json')
        def manifest_json():
            return get_file('chrome-llm/manifest.json')

        self.add_route_get(service_worker_js)
        self.add_route_get(manifest_json)


    def setup_static_routes(self):
        path_static_folder  = mgraph_ai_ui_html_transformation_workbench__ui.path
        path_static         = f"/{UI__CONSOLE__ROUTE__CONSOLE}"
        path_name           = UI__CONSOLE__ROUTE__CONSOLE
        major_version       = UI__CONSOLE__MAJOR__VERSION
        latest_version      = UI__CONSOLE__LATEST__VERSION
        start_page          = UI__CONSOLE__ROUTE__START_PAGE
        path_latest_version = f"/{path_name}/{major_version}/{latest_version}/{start_page}.html"
        self.app().mount(path_static, StaticFiles(directory=path_static_folder), name=path_name)


        @route_path(path=f'/{UI__CONSOLE__ROUTE__CONSOLE}')
        def redirect_to_latest():
            return RedirectResponse(url=path_latest_version)

        self.add_route_get(redirect_to_latest)
