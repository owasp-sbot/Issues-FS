# ═══════════════════════════════════════════════════════════════════════════════
# MGraph__Issues__Sync__Service - Syncs filesystem to MGraphDB
# Phase 2 (B19): Handles lazy loading, root changes, and persistence
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import Dict
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                   import type_safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                import Edge_Id
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text     import Safe_Str__Text
from osbot_utils.utils.Json                                                      import json_dumps, json_loads
from mgraph_ai_ui_html_transformation_workbench.mgraph.Schema__MGraph__Issues    import Schema__MGraph__Issue__Node, Schema__MGraph__Issue__Edge
from mgraph_ai_ui_html_transformation_workbench.mgraph.MGraph__Issues__Domain    import MGraph__Issues__Domain
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository import Graph__Repository
from mgraph_ai_ui_html_transformation_workbench.service.issues.storage.Path__Handler__Graph_Node import Path__Handler__Graph_Node
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types import Safe_Str__Node_Label, Safe_Str__Node_Type, Safe_Str__Status


class MGraph__Issues__Sync__Service(Type_Safe):                                  # Sync service
    graph        : MGraph__Issues__Domain        = None                          # Graph domain object
    repository   : Graph__Repository                                             # Data access
    path_handler : Path__Handler__Graph_Node                                     # Path generation
    is_loaded    : bool                          = False                         # Lazy load flag
    current_root : Safe_Str__File__Path          = None                          # Current root filter

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.graph is None:
            self.graph = MGraph__Issues__Domain()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Lazy Loading
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def ensure_loaded(self                                       ,               # Lazy load graph
                      root : Safe_Str__File__Path = None
                 ) -> MGraph__Issues__Domain:
        root_str    = str(root) if root else ''
        current_str = str(self.current_root) if self.current_root else ''

        if self.is_loaded is False or root_str != current_str:
            self.full_sync(root)

        return self.graph

    @type_safe
    def on_root_change(self, new_root: Safe_Str__File__Path) -> None:            # Root change trigger
        new_root_str = str(new_root) if new_root else ''
        current_str  = str(self.current_root) if self.current_root else ''

        if new_root_str != current_str:
            self.full_sync(new_root)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Full Sync
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def full_sync(self                                       ,                   # Rebuild graph from filesystem
                  root : Safe_Str__File__Path = None
             ) -> Dict:
        self.graph.clear()
        self.current_root = root

        nodes = self.repository.nodes_list_all(root_path=root)
        stats = {'nodes_added': 0, 'edges_added': 0}

        # Add all nodes
        for info in nodes:
            node_data = self.repository.node_load_by_path(info.path)

            if node_data is None:
                continue

            # Extract node_id, use existing or generate new
            node_id = Node_Id()
            if hasattr(node_data, 'node_id') and node_data.node_id:
                node_id = node_data.node_id

            graph_node = Schema__MGraph__Issue__Node(
                node_id   = node_id                                              ,
                label     = node_data.label                                      ,
                title     = Safe_Str__Text(str(node_data.title))                 ,
                node_type = node_data.node_type                                  ,
                status    = node_data.status if node_data.status else Safe_Str__Status(''),
                file_path = info.path                                            )

            self.graph.add_node(graph_node)
            stats['nodes_added'] += 1

        # Build containment edges from path structure
        edges_added = self.build_containment_edges()
        stats['edges_added'] = edges_added

        # Persist to disk
        self.save_to_disk()
        self.is_loaded = True

        return stats

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Building
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def build_containment_edges(self) -> int:                                    # Infer parent-child from paths
        edges_added = 0

        for node_id, node in self.graph.data.nodes.items():
            parent_path = self.infer_parent_path(str(node.file_path))

            if parent_path is None:
                continue

            parent_node = self.graph.get_node_by_path(parent_path)

            if parent_node is None:
                continue

            edge = Schema__MGraph__Issue__Edge(
                edge_id   = Edge_Id()                                            ,
                source_id = parent_node.node_id                                  ,
                target_id = node.node_id                                         ,
                edge_type = Safe_Str__Text('contains')                           )

            self.graph.add_edge(edge)
            edges_added += 1

        return edges_added

    @type_safe
    def infer_parent_path(self, child_path: str) -> str:                         # Extract parent path
        """
        From 'data/project/Project-1/issues/Version-1'
        returns 'data/project/Project-1'

        From 'data/project/Project-1/issues/Version-1/issues/Task-6'
        returns 'data/project/Project-1/issues/Version-1'
        """
        if '/issues/' not in child_path:
            return None

        parts = child_path.rsplit('/issues/', 1)

        if len(parts) == 2:
            return parts[0]

        return None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Persistence
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def get_index_path(self) -> str:                                             # Get path for index file
        base_path = str(self.path_handler.base_path) if self.path_handler.base_path else ''

        if base_path and base_path != '.':
            return f"{base_path}/indexes/issues.mgraph.json"
        else:
            return "indexes/issues.mgraph.json"

    @type_safe
    def save_to_disk(self) -> bool:                                              # Persist to indexes/
        path = self.get_index_path()

        # Serialize graph data
        nodes_data = {}
        for node_id, node in self.graph.data.nodes.items():
            nodes_data[node_id] = node.json()

        edges_data = {}
        for edge_id, edge in self.graph.data.edges.items():
            edges_data[edge_id] = edge.json()

        data = {
            'nodes': nodes_data,
            'edges': edges_data,
        }

        content = json_dumps(data, indent=2)
        return self.repository.storage_fs.file__save(path, content.encode('utf-8'))

    @type_safe
    def load_from_disk(self) -> bool:                                            # Load from indexes/
        path = self.get_index_path()

        if self.repository.storage_fs.file__exists(path) is False:
            return False

        content = self.repository.storage_fs.file__str(path)
        if not content:
            return False

        data = json_loads(content)
        if data is None:
            return False

        self.graph.clear()

        # Deserialize nodes
        for node_id, node_data in data.get('nodes', {}).items():
            node = Schema__MGraph__Issue__Node.from_json(node_data)
            self.graph.add_node(node)

        # Deserialize edges
        for edge_id, edge_data in data.get('edges', {}).items():
            edge = Schema__MGraph__Issue__Edge.from_json(edge_data)
            self.graph.add_edge(edge)

        self.is_loaded = True
        return True
