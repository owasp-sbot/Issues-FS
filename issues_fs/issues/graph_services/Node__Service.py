# ═══════════════════════════════════════════════════════════════════════════════
# Node__Service - Business logic for node operations
# Handles create, update, delete, and query operations for graph nodes
#
# Phase 2 Changes:
#   - B11: get_node_by_path() for loading by explicit folder path
#   - B14: resolve_hierarchical_path(), get_node_by_hierarchical_path()
#   - B17: list_nodes() respects root scoping via root_selection_service
#   - B22: parse_label_to_type(), type_to_label_prefix() for hyphenated labels
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                             import List, Optional
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                       import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                        import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                        import Timestamp_Now
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                      import Safe_Str__Node_Type, Safe_Str__Node_Label
from issues_fs.schemas.graph.Schema__Global__Index                                                      import Schema__Global__Index
from issues_fs.schemas.graph.Schema__Graph__Link                                                        import Schema__Graph__Link
from issues_fs.schemas.graph.Schema__Graph__Node                                                        import Schema__Graph__Node
from issues_fs.schemas.graph.Schema__Graph__Response                                                    import Schema__Graph__Response
from issues_fs.schemas.graph.Schema__Node                                                               import Schema__Node
from issues_fs.schemas.graph.Schema__Node__Create__Request                                              import Schema__Node__Create__Request
from issues_fs.schemas.graph.Schema__Node__Create__Response                                             import Schema__Node__Create__Response
from issues_fs.schemas.graph.Schema__Node__Delete__Response                                             import Schema__Node__Delete__Response
from issues_fs.schemas.graph.Schema__Node__Link                                                         import Schema__Node__Link
from issues_fs.schemas.graph.Schema__Node__List__Response                                               import Schema__Node__List__Response
from issues_fs.schemas.graph.Schema__Node__Response                                                     import Schema__Node__Response
from issues_fs.schemas.graph.Schema__Node__Summary                                                      import Schema__Node__Summary
from issues_fs.schemas.graph.Schema__Node__Update__Request                                              import Schema__Node__Update__Request
from issues_fs.schemas.graph.Schema__Node__Update__Response                                             import Schema__Node__Update__Response
from issues_fs.schemas.graph.Schema__Type__Summary                                                      import Schema__Type__Summary
from issues_fs.issues.graph_services.Graph__Repository                                                  import Graph__Repository


# todo: refactor to Issue__Node__Service
#       root_selection_service should not be an object
class Node__Service(Type_Safe):                                                  # Node business logic service
    repository             : Graph__Repository                                   # Data access layer
    root_selection_service : object            = None                             # Phase 2 (B14/B17): Root context

    # ═══════════════════════════════════════════════════════════════════════════════
    # Query Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_node(self                              ,                             # Get single node by label
                 node_type : Safe_Str__Node_Type   ,
                 label     : Safe_Str__Node_Label
            ) -> Optional[Schema__Node]:
        return self.repository.node_load(node_type = node_type ,
                                         label     = label     )

    def node_exists(self                              ,                          # Check if node exists
                    node_type : Safe_Str__Node_Type   ,
                    label     : Safe_Str__Node_Label
               ) -> bool:
        return self.repository.node_exists(node_type = node_type ,
                                           label     = label     )

    def list_nodes(self                                       ,                  # List nodes, optionally filtered by type
                   node_type : Safe_Str__Node_Type = None
              ) -> Schema__Node__List__Response:
        current_root = self.get_current_root_path()                              # Phase 2 (B17): Get root filter
        summaries    = []

        if node_type:
            summaries = self.list_nodes_for_type(node_type, current_root)
        else:
            node_types = self.repository.node_types_load()
            for nt in node_types:
                type_summaries = self.list_nodes_for_type(nt.name, current_root)
                summaries.extend(type_summaries)

        return Schema__Node__List__Response(success = True           ,
                                            nodes   = summaries      ,
                                            total   = len(summaries) )

    def list_nodes_for_type(self                                       ,         # List nodes for specific type
                            node_type    : Safe_Str__Node_Type         ,
                            root_path    : Safe_Str__File__Path = None
                       ) -> List[Schema__Node__Summary]:
        summaries = []
        all_nodes = self.repository.nodes_list_all(root_path=root_path)          # Phase 2 (B10/B17): Recursive with filter

        for node_info in all_nodes:
            if str(node_info.node_type) != str(node_type):
                continue

            node = self.repository.node_load_by_path(node_info.path)
            if node:
                summary = Schema__Node__Summary(label     = node.label     ,
                                                node_type = node.node_type ,
                                                title     = node.title     ,
                                                status    = node.status    )
                summaries.append(summary)

        return summaries

    def get_current_root_path(self) -> Safe_Str__File__Path:                     # Phase 2 (B17): Get current root
        if self.root_selection_service is None:
            return None

        root_str = str(self.root_selection_service.current_root)
        if root_str:
            return Safe_Str__File__Path(root_str)

        return None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Path-Based Loading - Phase 2 (B11)
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def get_node_by_path(self                              ,                     # Get by explicit folder path
                         folder_path : Safe_Str__File__Path
                    ) -> Schema__Node__Response:
        node = self.repository.node_load_by_path(folder_path)

        if node is not None:
            return Schema__Node__Response(success = True ,
                                          node    = node )

        return Schema__Node__Response(success = False                              ,
                                      message = f'Node not found at: {folder_path}')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def create_node(self                                       ,                 # Create new node
                    request : Schema__Node__Create__Request
               ) -> Schema__Node__Create__Response:
        # Validate title is not empty
        if str(request.title).strip() == '':
            return Schema__Node__Create__Response(success = False               ,
                                                  message = 'Title is required' )

        # Validate node type exists
        node_types = self.repository.node_types_load()
        node_type_def = None
        for nt in node_types:
            if str(nt.name) == str(request.node_type):
                node_type_def = nt
                break

        if node_type_def is None:
            return Schema__Node__Create__Response(success = False                              ,
                                                  message = f'Unknown node type: {request.node_type}')

        # Get next index for this type
        type_index = self.repository.type_index_load(request.node_type)
        next_num   = int(type_index.next_index)
        label      = self.label_from_type_and_index(request.node_type, next_num)

        # SAFETY CHECK: If label already exists, find actual next available index
        while self.repository.node_exists(node_type=request.node_type, label=label):
            next_num += 1
            label = self.label_from_type_and_index(request.node_type, next_num)

        now = Timestamp_Now()

        # Determine status
        status = request.status if request.status else node_type_def.default_status

        # Create node
        node = Schema__Node(node_id     = Obj_Id()                               ,
                            node_type   = request.node_type                      ,
                            node_index  = Safe_UInt(next_num)                    ,
                            label       = label                                  ,
                            title       = request.title                          ,
                            description = request.description                    ,
                            status      = status                                 ,
                            created_at  = now                                    ,
                            updated_at  = now                                    ,
                            created_by  = Obj_Id()                               ,  # TODO: actual creator
                            tags        = list(request.tags) if request.tags else [],
                            links       = []                                     ,
                            properties  = dict(request.properties) if request.properties else {})

        # Save node
        if self.repository.node_save(node) is False:
            return Schema__Node__Create__Response(success = False               ,
                                                  message = 'Failed to save node')

        # Update type index
        type_index.next_index   = Safe_UInt(next_num + 1)
        type_index.count        = Safe_UInt(int(type_index.count) + 1)
        type_index.last_updated = now
        self.repository.type_index_save(type_index)

        # Update global index
        self.update_global_index()

        return Schema__Node__Create__Response(success = True ,
                                              node    = node )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Update Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def update_node(self                              ,                          # Update existing node
                    node_type : Safe_Str__Node_Type   ,
                    label     : Safe_Str__Node_Label  ,
                    request   : Schema__Node__Update__Request
               ) -> Schema__Node__Update__Response:
        node = self.repository.node_load(node_type = node_type ,
                                         label     = label     )
        if node is None:
            return Schema__Node__Update__Response(success = False                    ,
                                                  message = f'Node not found: {label}')

        # Apply updates - use truthiness check because Type_Safe auto-initializes
        # empty strings for Safe_Str types (so `is not None` doesn't work)
        if request.title:                                                        # Only update if non-empty
            node.title = request.title
        if request.description:                                                  # Only update if non-empty
            node.description = request.description
        if request.status:                                                       # Only update if non-empty
            node.status = request.status
        if request.tags is not None:                                             # Tags can be empty list
            node.tags = list(request.tags)
        if request.properties is not None:                                       # Deep merge properties
            node.properties = self.deep_merge_properties(node.properties, request.properties)

        node.updated_at = Timestamp_Now()

        # Save
        if self.repository.node_save(node) is False:
            return Schema__Node__Update__Response(success = False                 ,
                                                  message = 'Failed to save node' )

        return Schema__Node__Update__Response(success = True ,
                                              node    = node )

    def deep_merge_properties(self                  ,                            # Deep merge properties dicts
                              existing : dict       ,
                              updates  : dict
                         ) -> dict:
        result = dict(existing) if existing else {}                              # Copy existing properties

        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge_properties(result[key], value)     # Recursively merge nested dicts
            else:
                result[key] = value                                              # Replace or add key

        return result

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def delete_node(self                              ,                          # Delete node
                    node_type : Safe_Str__Node_Type   ,
                    label     : Safe_Str__Node_Label
               ) -> Schema__Node__Delete__Response:
        if self.repository.node_exists(node_type, label) is False:
            return Schema__Node__Delete__Response(success = False                     ,
                                                  deleted = False                     ,
                                                  label   = label                     ,
                                                  message = f'Node not found: {label}')

        # TODO: Remove links from other nodes pointing to this one

        # Delete node
        if self.repository.node_delete(node_type, label) is False:
            return Schema__Node__Delete__Response(success = False                   ,
                                                  deleted = False                   ,
                                                  label   = label                   ,
                                                  message = 'Failed to delete node' )

        # Update type index
        type_index = self.repository.type_index_load(node_type)
        type_index.count = Safe_UInt(max(0, int(type_index.count) - 1))
        type_index.last_updated = Timestamp_Now()
        self.repository.type_index_save(type_index)

        # Update global index
        self.update_global_index()

        return Schema__Node__Delete__Response(success = True  ,
                                              deleted = True  ,
                                              label   = label )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Label Generation - Phase 2 (B22): Hyphenated Labels
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def label_from_type_and_index(self                              ,            # Generate hyphenated label
                                  node_type  : Safe_Str__Node_Type  ,
                                  node_index : int
                             ) -> Safe_Str__Node_Label:
        display_type = self.type_to_label_prefix(node_type)
        return f"{display_type}-{node_index}"

    def type_to_label_prefix(self, node_type: str) -> str:                       # Phase 2 (B22): Convert type to prefix
        return '-'.join(word.capitalize() for word in node_type.split('-'))

    @type_safe
    def parse_label_to_type(self                              ,                  # Phase 2 (B22): Extract type from label
                            label : Safe_Str__Node_Label
                       ) -> Safe_Str__Node_Type:
        label_str   = str(label)
        known_types = [str(nt.name) for nt in self.repository.node_types_load()]

        for node_type in sorted(known_types, key=len, reverse=True):             # Longest first so 'user-story' matches before 'user'
            prefix = self.type_to_label_prefix(node_type)

            if label_str.startswith(f"{prefix}-"):
                return node_type

        # Fallback: assume single-word type (first segment before hyphen)
        if '-' in label_str:
            type_part = label_str.split('-', 1)[0].lower()
            return type_part

        return None

    def update_global_index(self) -> None:                                       # Recalculate global index
        node_types   = self.repository.node_types_load()
        total_nodes  = 0
        type_counts  = []

        for nt in node_types:
            type_index = self.repository.type_index_load(nt.name)
            count      = int(type_index.count)
            total_nodes += count
            type_counts.append(Schema__Type__Summary(node_type = nt.name          ,
                                                     count     = Safe_UInt(count) ))

        global_index = Schema__Global__Index(total_nodes  = Safe_UInt(total_nodes) ,
                                             last_updated = Timestamp_Now()        ,
                                             type_counts  = type_counts            )

        self.repository.global_index_save(global_index)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Graph Traversal Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_node_graph(self                              ,                       # Get node with connected nodes
                       node_type : Safe_Str__Node_Type   ,
                       label     : Safe_Str__Node_Label  ,
                       depth     : int = 1
                  ) -> Schema__Graph__Response:

        if depth > 3:                                                            # Cap depth to prevent expensive traversals
            depth = 3

        root_node = self.repository.node_load(node_type = node_type ,
                                              label     = label     )
        if root_node is None:
            return Schema__Graph__Response(success = False              ,
                                           root    = label              ,
                                           nodes   = []                 ,
                                           links   = []                 ,
                                           depth   = depth              ,
                                           message = f'Node not found: {label}')

        visited_labels = set()
        nodes          = []
        links          = []

        self.traverse_graph(root_node, depth, visited_labels, nodes, links)

        return Schema__Graph__Response(success = True   ,
                                       root    = label  ,
                                       nodes   = nodes  ,
                                       links   = links  ,
                                       depth   = depth  )

    def traverse_graph(self                       ,                              # Recursively traverse graph
                       node    : Schema__Node     ,
                       depth   : int              ,
                       visited : set              ,
                       nodes   : list             ,
                       links   : list
                  ) -> None:

        label_str = str(node.label)
        if label_str in visited or depth < 0:
            return

        visited.add(label_str)
        nodes.append(Schema__Graph__Node(label     = node.label     ,
                                         title     = node.title     ,
                                         node_type = node.node_type ,
                                         status    = node.status    ))

        if depth == 0:
            return

        # Traverse outgoing links
        if node.links:
            for link in node.links:
                target_label = link.target_label
                if target_label and str(target_label) not in visited:
                    target_node = self.resolve_link_target(link)
                    if target_node:
                        links.append(Schema__Graph__Link(source    = node.label      ,
                                                         target    = target_node.label,
                                                         link_type = link.verb))
                        self.traverse_graph(target_node, depth - 1, visited, nodes, links)

        # Find and traverse incoming links
        incoming = self.find_incoming_links(node.label)
        for source_node, link_type in incoming:
            if str(source_node.label) not in visited:
                links.append(Schema__Graph__Link(source    = source_node.label ,
                                                 target    = node.label        ,
                                                 link_type = link_type         ))
                self.traverse_graph(source_node, depth - 1, visited, nodes, links)

    def resolve_link_target(self                           ,                     # Phase 2 (B22): Load target from link
                            link : Schema__Node__Link
                       ) -> Schema__Node:
        if not link.target_label:
            return None

        target_label = link.target_label
        target_type  = self.parse_label_to_type(target_label)                    # Phase 2: Use new parser

        if target_type is None:
            return None

        try:
            return self.repository.node_load(node_type = target_type  ,
                                             label     = target_label )
        except Exception:
            return None

    # todo: this should not be a tuple, this should be a Type_Safe class
    def find_incoming_links(self                              ,                  # Find nodes that link TO this node
                            label : Safe_Str__Node_Label
                       ) -> List[tuple]:
        incoming    = []
        label_str   = str(label)
        node_types  = self.repository.node_types_load()

        for nt in node_types:
            labels = self.repository.nodes_list_labels(nt.name)
            for node_label in labels:
                if str(node_label) == label_str:                                 # Skip self
                    continue

                node = self.repository.node_load(node_type = nt.name   ,
                                                 label     = node_label)
                if node and node.links:
                    for link in node.links:
                        if link.target_label and str(link.target_label) == label_str:
                            incoming.append((node, str(link.verb)))
                            break                                                # Only add node once

        return incoming
