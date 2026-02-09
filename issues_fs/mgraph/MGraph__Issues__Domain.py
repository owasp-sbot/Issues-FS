# ═══════════════════════════════════════════════════════════════════════════════
# MGraph__Issues__Domain - Business logic for issue graph operations
# Phase 2 (B18): Four-layer architecture - Domain Layer
#
# Contains indexes and query methods - operates on Schema__MGraph__Issues__Data
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                         import Dict, List
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                      import type_safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                   import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                                   import Edge_Id
from issues_fs.mgraph.Schema__MGraph__Issues                                                        import Schema__MGraph__Issue__Node, Schema__MGraph__Issue__Edge, Schema__MGraph__Issues__Data
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                  import Safe_Str__Node_Label


class MGraph__Issues__Domain(Type_Safe):                                     # Graph domain operations
    data            : Schema__MGraph__Issues__Data                                # Underlying data
    index_by_label  : Dict[str, str]                                             # label -> node_id (index, not persisted)  # Bug-8: use Safe_Str__Node_Label/Node_Id
    index_by_path   : Dict[str, str]                                             # path -> node_id (index, not persisted)   # Bug-8: use Safe_Str__File__Path/Node_Id
    index_by_parent : Dict[str, List[str]]                                       # parent_id -> [child_ids] (index)         # Bug-8: use Node_Id keys/values

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def add_node(self, node: Schema__MGraph__Issue__Node) -> str:                # Add node and update indexes
        node_id_str = str(node.node_id)

        self.data.nodes[node_id_str] = node
        self.index_by_label[str(node.label)]    = node_id_str                    # Update label index
        self.index_by_path[str(node.file_path)] = node_id_str                    # Update path index

        return node_id_str

    @type_safe
    def get_node_by_label(self                              ,                    # Query by label
                          label : Safe_Str__Node_Label
                     ) -> Schema__MGraph__Issue__Node:
        node_id = self.index_by_label.get(str(label))

        if node_id is None:
            return None

        return self.data.nodes.get(node_id)

    @type_safe
    def get_node_by_path(self, path: str) -> Schema__MGraph__Issue__Node:        # Query by file path
        node_id = self.index_by_path.get(path)

        if node_id is None:
            return None

        return self.data.nodes.get(node_id)

    @type_safe
    def get_node_by_id(self, node_id: str) -> Schema__MGraph__Issue__Node:       # Query by ID
        return self.data.nodes.get(node_id)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def add_edge(self, edge: Schema__MGraph__Issue__Edge) -> str:                # Add edge and update indexes
        edge_id_str   = str(edge.edge_id)                                        # Bug-8: str() cascade from raw Dict keys
        source_id_str = str(edge.source_id)
        target_id_str = str(edge.target_id)

        self.data.edges[edge_id_str] = edge
        if str(edge.edge_type) == 'contains':                                    # Update parent-child index for 'contains' edges
            if source_id_str not in self.index_by_parent:
                self.index_by_parent[source_id_str] = []
            if target_id_str not in self.index_by_parent[source_id_str]:
                self.index_by_parent[source_id_str].append(target_id_str)

        return edge_id_str

    @type_safe
    def get_children(self, parent_id: Node_Id) -> List[Schema__MGraph__Issue__Node]:
        parent_id_str = str(parent_id)
        child_ids     = self.index_by_parent.get(parent_id_str, [])

        children = []
        for child_id in child_ids:
            child_node = self.data.nodes.get(child_id)
            if child_node is not None:
                children.append(child_node)

        return children

    @type_safe
    def get_children_by_label(self                              ,                # Get children by parent label
                              label : Safe_Str__Node_Label
                         ) -> List[Schema__MGraph__Issue__Node]:
        node = self.get_node_by_label(label)
        if node is None:
            return []
        return self.get_children(node.node_id)

    @type_safe
    def get_ancestors(self                     ,                                 # Get path to root
                      node_id : Node_Id
                 ) -> List[Schema__MGraph__Issue__Node]:
        ancestors     = []
        current_id    = str(node_id)
        visited       = set()

        while current_id and current_id not in visited:
            visited.add(current_id)

            # Find parent edge (where this node is the target)
            parent_id = None
            for edge in self.data.edges.values():
                if str(edge.edge_type) == 'contains' and str(edge.target_id) == current_id:
                    parent_id = str(edge.source_id)
                    break

            if parent_id is None:
                break

            parent_node = self.data.nodes.get(parent_id)
            if parent_node is not None:
                ancestors.append(parent_node)

            current_id = parent_id

        return ancestors

    @type_safe
    def get_ancestors_by_label(self                              ,               # Get ancestors by node label
                               label : Safe_Str__Node_Label
                          ) -> List[Schema__MGraph__Issue__Node]:
        node = self.get_node_by_label(label)
        if node is None:
            return []
        return self.get_ancestors(node.node_id)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Utility Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def clear(self) -> None:                                                     # Reset all data and indexes
        self.data.nodes.clear()
        self.data.edges.clear()
        self.index_by_label.clear()
        self.index_by_path.clear()
        self.index_by_parent.clear()

    def all_nodes(self) -> List[Schema__MGraph__Issue__Node]:                    # Get all nodes
        return list(self.data.nodes.values())

    def all_edges(self) -> List[Schema__MGraph__Issue__Edge]:                    # Get all edges
        return list(self.data.edges.values())

    def node_count(self) -> int:                                                 # Total node count
        return len(self.data.nodes)

    def edge_count(self) -> int:                                                 # Total edge count
        return len(self.data.edges)
