# ═══════════════════════════════════════════════════════════════════════════════
# Routes__Graph - MGraphDB query and visualization endpoints
# Phase 2 (B20, B21): Query endpoints and D3/force-directed formats
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import Dict, List
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_fast_api.api.Fast_API__Routes                                         import Fast_API__Routes
from osbot_fast_api.api.decorators.route_path                                    import route_path
from mgraph_ai_ui_html_transformation_workbench.services.mgraph.MGraph__Issues__Sync__Service import MGraph__Issues__Sync__Service
from mgraph_ai_ui_html_transformation_workbench.mgraph.MGraph__Issues__Domain    import MGraph__Issues__Domain


TAG__ROUTES_GRAPH = 'graph'


class Routes__Graph(Fast_API__Routes):                                           # Graph query routes
    tag          : str                           = TAG__ROUTES_GRAPH
    sync_service : MGraph__Issues__Sync__Service

    # ═══════════════════════════════════════════════════════════════════════════════
    # Query Endpoints (B20)
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/api/graph/nodes')
    def list_nodes(self) -> Dict:                                                # GET: All nodes
        graph = self.sync_service.ensure_loaded()
        nodes = [n.json() for n in graph.all_nodes()]
        return {'success': True, 'nodes': nodes, 'total': len(nodes)}

    @route_path('/api/graph/node/{label}')
    def get_node(self, label: str) -> Dict:                                      # GET: Single node
        graph = self.sync_service.ensure_loaded()
        node  = graph.get_node_by_label(label)

        if node is not None:
            return {'success': True, 'node': node.json()}

        return {'success': False, 'message': f'Node not found: {label}'}

    @route_path('/api/graph/node/{label}/children')
    def get_children(self, label: str) -> Dict:                                  # GET: Direct children
        graph = self.sync_service.ensure_loaded()
        node  = graph.get_node_by_label(label)

        if node is None:
            return {'success': False, 'message': f'Node not found: {label}'}

        children = graph.get_children(node.node_id)
        return {
            'success': True,
            'nodes'  : [c.json() for c in children],
            'total'  : len(children)
        }

    @route_path('/api/graph/node/{label}/ancestors')
    def get_ancestors(self, label: str) -> Dict:                                 # GET: Path to root
        graph = self.sync_service.ensure_loaded()
        node  = graph.get_node_by_label(label)

        if node is None:
            return {'success': False, 'message': f'Node not found: {label}'}

        ancestors = graph.get_ancestors(node.node_id)
        return {
            'success': True,
            'nodes'  : [a.json() for a in ancestors],
            'total'  : len(ancestors)
        }

    @route_path('/api/graph/sync')
    def force_sync(self) -> Dict:                                                # POST: Force resync
        stats = self.sync_service.full_sync(root=self.sync_service.current_root)
        return {'success': True, 'stats': stats}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Visualization Endpoints (B21)
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/api/graph/viz/tree')
    def get_viz_tree(self, root: str = None) -> Dict:                            # GET: D3 tree format
        """
        Returns hierarchical tree format for D3.js.

        Response:
        {
          "name": "Project-1",
          "title": "GitGraph Issues",
          "type": "project",
          "children": [...]
        }
        """
        graph = self.sync_service.ensure_loaded()

        if root:
            root_node = graph.get_node_by_label(root)
        else:
            root_node = self.find_root_node(graph)

        if root_node is None:
            return {'success': False, 'message': 'No root found'}

        tree = self.build_tree_recursive(graph, root_node)
        return {'success': True, 'tree': tree}

    @route_path('/api/graph/viz/force')
    def get_viz_force(self) -> Dict:                                             # GET: Force-directed format
        """
        Returns force-directed graph format for D3/vis.js.

        Response:
        {
          "nodes": [{"id": "Project-1", "label": "...", "type": "...", "group": 1}],
          "links": [{"source": "Project-1", "target": "Version-1", "type": "contains"}]
        }
        """
        graph = self.sync_service.ensure_loaded()

        nodes = []
        links = []
        type_groups = {}
        group_counter = 0

        # Build nodes with group assignments by type
        for node in graph.all_nodes():
            node_type = str(node.node_type)
            if node_type not in type_groups:
                type_groups[node_type] = group_counter
                group_counter += 1

            nodes.append({
                'id'    : str(node.label),
                'label' : str(node.title),
                'type'  : node_type,
                'status': str(node.status) if node.status else '',
                'group' : type_groups[node_type]
            })

        # Build links from edges
        for edge in graph.all_edges():
            source_node = graph.get_node_by_id(str(edge.source_id))
            target_node = graph.get_node_by_id(str(edge.target_id))

            if source_node and target_node:
                links.append({
                    'source': str(source_node.label),
                    'target': str(target_node.label),
                    'type'  : str(edge.edge_type)
                })

        return {'success': True, 'nodes': nodes, 'links': links}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def find_root_node(self, graph: MGraph__Issues__Domain):                     # Find node with no parent
        """Find a node that is not the target of any 'contains' edge."""
        all_targets = set()

        for edge in graph.all_edges():
            if str(edge.edge_type) == 'contains':
                all_targets.add(str(edge.target_id))

        for node_id, node in graph.data.nodes.items():
            if node_id not in all_targets:
                return node

        # If no root found, return first node
        nodes = graph.all_nodes()
        return nodes[0] if nodes else None

    def build_tree_recursive(self                                ,               # Build D3 tree structure
                             graph : MGraph__Issues__Domain      ,
                             node
                        ) -> Dict:
        children     = graph.get_children(node.node_id)
        child_trees  = [self.build_tree_recursive(graph, c) for c in children]

        return {
            'name'    : str(node.label),
            'title'   : str(node.title),
            'type'    : str(node.node_type),
            'status'  : str(node.status) if node.status else '',
            'children': child_trees
        }

    # ═══════════════════════════════════════════════════════════════════════════════
    # Route Setup
    # ═══════════════════════════════════════════════════════════════════════════════

    def setup_routes(self):                                                      # Configure all routes
        self.add_route_get (self.list_nodes   )
        self.add_route_get (self.get_node     )
        self.add_route_get (self.get_children )
        self.add_route_get (self.get_ancestors)
        self.add_route_post(self.force_sync   )
        self.add_route_get (self.get_viz_tree )
        self.add_route_get (self.get_viz_force)
        return self
