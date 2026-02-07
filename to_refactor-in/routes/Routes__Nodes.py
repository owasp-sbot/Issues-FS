# ═══════════════════════════════════════════════════════════════════════════════
# Routes__Nodes - REST API for graph node operations
# Provides endpoints for node create, read, update, delete
#
# Phase 2 Changes:
#   - B14: Added /api/nodes/by-path endpoint for hierarchical path resolution
#
# Path pattern: /api/nodes/...
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                                            import HTTPException
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types                     import Safe_Str__Node_Type, Safe_Str__Node_Label
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Graph__Response                   import Schema__Graph__Response
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Create__Request             import Schema__Node__Create__Request
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Create__Response            import Schema__Node__Create__Response
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Delete__Response            import Schema__Node__Delete__Response
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__List__Response              import Schema__Node__List__Response
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Response                    import Schema__Node__Response
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Update__Request             import Schema__Node__Update__Request
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Update__Response            import Schema__Node__Update__Response
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Node__Service             import Node__Service
from osbot_fast_api.api.decorators.route_path                                                           import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                                         import Fast_API__Routes
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node                              import Schema__Node


TAG__ROUTES_NODES = 'nodes'

ROUTES_PATHS__NODES = [f'/nodes/{TAG__ROUTES_NODES}'                               ,
                       f'/nodes/{TAG__ROUTES_NODES}/{{label}}'                     ,
                       f'/nodes/{TAG__ROUTES_NODES}/type/{{node_type}}'            ,
                       f'/nodes/{TAG__ROUTES_NODES}/by-path'                       ]  # Phase 2


class Routes__Nodes(Fast_API__Routes):                                           # Node routes
    tag     : str          = TAG__ROUTES_NODES                                   # Route tag
    service : Node__Service                                                      # Node service

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/api/nodes')
    def nodes(self) -> Schema__Node__List__Response:                             # GET /api/nodes
        return self.service.list_nodes()

    @route_path('/api/nodes/type/{node_type}')
    def nodes__by_type(self                            ,                         # GET /api/nodes/type/{node_type}
                       node_type : Safe_Str__Node_Type
                  ) -> Schema__Node__List__Response:
        return self.service.list_nodes(node_type=node_type)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create Operation
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/api/nodes')
    def node__create(self                                       ,                # POST /api/nodes
                     request : Schema__Node__Create__Request
                ) -> Schema__Node__Create__Response:
        response = self.service.create_node(request)
        if response.success is False:
            raise HTTPException(status_code = 400              ,
                                detail      = response.message )
        return response

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/api/nodes/{label}')
    def node__get(self                             ,                             # GET /api/nodes/{label}
                  label : Safe_Str__Node_Label
             ) -> Schema__Node:
        # Parse label to get type
        node_type = self.parse_label_type(label)
        if node_type is None:
            raise HTTPException(status_code = 400                       ,
                                detail      = f'Invalid label: {label}' )

        node = self.service.get_node(node_type = node_type ,
                                     label     = label     )
        if node is None:
            raise HTTPException(status_code = 404                      ,
                                detail      = f'Node not found: {label}')
        return node

    @route_path('/api/nodes/by-path')
    def node__get_by_path(self, path: str) -> Schema__Node__Response:            # Phase 2 (B14): GET /api/nodes/by-path?path=...
        """
        Get node by hierarchical path.

        Examples:
          /api/nodes/by-path?path=Project-1
          /api/nodes/by-path?path=Project-1/Version-1
          /api/nodes/by-path?path=Project-1/Version-1/Task-6

        When root is set, paths are relative to root:
          (root=data/project/Project-1)
          /api/nodes/by-path?path=Version-1  → loads Project-1/issues/Version-1
        """
        if not path:
            raise HTTPException(status_code = 400                              ,
                                detail      = 'Path parameter is required'     )

        response = self.service.get_node_by_hierarchical_path(path)

        if response.success is False:
            raise HTTPException(status_code = 404              ,
                                detail      = response.message )

        return response

    # ═══════════════════════════════════════════════════════════════════════════════
    # Update Operation
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/api/nodes/{label}')
    def node__update(self                                       ,                # PATCH /api/nodes/{label}
                     label   : Safe_Str__Node_Label             ,
                     request : Schema__Node__Update__Request
                ) -> Schema__Node__Update__Response:
        node_type = self.parse_label_type(label)
        if node_type is None:
            raise HTTPException(status_code = 400                       ,
                                detail      = f'Invalid label: {label}' )

        response = self.service.update_node(node_type = node_type ,
                                            label     = label     ,
                                            request   = request   )
        if response.success is False:
            raise HTTPException(status_code = 404              ,
                                detail      = response.message )
        return response

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Operation
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/api/nodes/{label}')
    def node__delete(self                             ,                          # DELETE /api/nodes/{label}
                     label : Safe_Str__Node_Label
                ) -> Schema__Node__Delete__Response:
        node_type = self.parse_label_type(label)
        if node_type is None:
            raise HTTPException(status_code = 400                       ,
                                detail      = f'Invalid label: {label}' )

        response = self.service.delete_node(node_type = node_type ,
                                            label     = label     )
        if response.success is False:
            raise HTTPException(status_code = 404              ,
                                detail      = response.message )
        return response

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def parse_label_type(self                             ,                      # Extract type from label (simple)
                         label : Safe_Str__Node_Label
                    ) -> Safe_Str__Node_Type:
        """
        Simple label parsing for routes. For complex hyphenated types,
        Node__Service.parse_label_to_type() should be used.
        """
        label_str = str(label)
        if '-' not in label_str:
            return None
        type_part = label_str.split('-', 1)[0].lower()
        try:
            return Safe_Str__Node_Type(type_part)
        except Exception:
            return None

    @route_path('/api/nodes/{node_type}/{label}/graph')
    def get_node_graph(self                              ,                       # Get node with connected nodes
                       node_type : Safe_Str__Node_Type   ,
                       label     : Safe_Str__Node_Label  ,
                       depth     : Safe_UInt             = 1
                  ) -> dict:
        try:
            response = self.service.get_node_graph(node_type = Safe_Str__Node_Type(node_type) ,
                                                   label     = Safe_Str__Node_Label(label)    ,
                                                   depth     = depth                          )
            return response.json()
        except Exception as e:
            return Schema__Graph__Response(success = False              ,
                                           message = f'Error: {str(e)}' ,
                                           nodes   = []                 ,
                                           links   = []                 ).json()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Route Setup
    # ═══════════════════════════════════════════════════════════════════════════════

    def setup_routes(self):                                                      # Configure all routes
        self.add_route_get   (self.nodes            )
        self.add_route_get   (self.nodes__by_type   )
        self.add_route_get   (self.node__get        )
        self.add_route_get   (self.node__get_by_path)                            # Phase 2 (B14)
        self.add_route_get   (self.get_node_graph   )
        self.add_route_post  (self.node__create     )
        self.add_route_patch (self.node__update     )
        self.add_route_delete(self.node__delete     )
        return self
