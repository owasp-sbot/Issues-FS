# ═══════════════════════════════════════════════════════════════════════════════
# Link__Service - Business logic for relationship operations
# Handles bidirectional link creation and deletion between nodes
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                             import Optional
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                        import Timestamp_Now
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe

from issues_fs.schemas.graph.Safe_Str__Graph_Types                     import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Link_Verb
from issues_fs.schemas.graph.Schema__Link__Create__Request             import Schema__Link__Create__Request
from issues_fs.schemas.graph.Schema__Link__Create__Response            import Schema__Link__Create__Response
from issues_fs.schemas.graph.Schema__Link__Delete__Response            import Schema__Link__Delete__Response
from issues_fs.schemas.graph.Schema__Link__List__Response              import Schema__Link__List__Response
from issues_fs.schemas.graph.Schema__Node__Link                        import Schema__Node__Link
from issues_fs.schemas.graph.Schema__Link__Type                        import Schema__Link__Type
from issues_fs.issues.graph_services.Graph__Repository         import Graph__Repository


class Link__Service(Type_Safe):                                                  # Link business logic service
    repository : Graph__Repository                                               # Data access layer

    # ═══════════════════════════════════════════════════════════════════════════════
    # Query Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def list_links(self                              ,                           # List links for a node
                   node_type : Safe_Str__Node_Type   ,
                   label     : Safe_Str__Node_Label
              ) -> Schema__Link__List__Response:
        node = self.repository.node_load(node_type = node_type ,
                                         label     = label     )
        if node is None:
            return Schema__Link__List__Response(success = False                     ,
                                                message = f'Node not found: {label}')

        return Schema__Link__List__Response(success = True       ,
                                            links   = node.links )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create Link Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def create_link(self                              ,                          # Create bidirectional link
                    source_type  : Safe_Str__Node_Type   ,
                    source_label : Safe_Str__Node_Label  ,
                    request      : Schema__Link__Create__Request                # todo: see if the source_type and source_label should not be defined inside the Schema__Link__Create__Request class
               ) -> Schema__Link__Create__Response:
        # Load source node
        source_node = self.repository.node_load(node_type = source_type  ,
                                                label     = source_label )
        if source_node is None:
            return Schema__Link__Create__Response(success = False                          ,
                                                  message = f'Source not found: {source_label}')

        # Parse target label to get type (e.g., "Bug-27" → "bug", "Bug-27")
        target_type, target_label = self.parse_label(request.target_label)
        if target_type is None:
            return Schema__Link__Create__Response(success = False                               ,
                                                  message = f'Invalid target label: {request.target_label}')

        # Load target node
        target_node = self.repository.node_load(node_type = target_type  ,
                                                label     = target_label )
        if target_node is None:
            return Schema__Link__Create__Response(success = False                          ,
                                                  message = f'Target not found: {target_label}')

        # Find link type definition
        link_type_def = self.find_link_type(request.verb)
        if link_type_def is None:
            return Schema__Link__Create__Response(success = False                           ,
                                                  message = f'Unknown link type: {request.verb}')

        # Validate source/target types are allowed
        if str(source_type) not in [str(t) for t in link_type_def.source_types]:
            return Schema__Link__Create__Response(success = False                                        ,
                                                  message = f'{source_type} cannot use verb {request.verb}')

        if str(target_type) not in [str(t) for t in link_type_def.target_types]:
            return Schema__Link__Create__Response(success = False                                        ,
                                                  message = f'{request.verb} cannot target {target_type}')

        now = Timestamp_Now()

        # Create forward link (source → target)
        source_link = Schema__Node__Link(link_type_id = link_type_def.link_type_id ,
                                         verb         = request.verb               ,
                                         target_id    = target_node.node_id        ,
                                         target_label = target_label               ,
                                         created_at   = now                        )

        # Create inverse link (target → source)
        target_link = Schema__Node__Link(link_type_id = link_type_def.link_type_id ,
                                         verb         = link_type_def.inverse_verb ,
                                         target_id    = source_node.node_id        ,
                                         target_label = source_label               ,
                                         created_at   = now                        )

        # Check for duplicate links
        for existing in source_node.links:
            if str(existing.target_id) == str(target_node.node_id) and str(existing.verb) == str(request.verb):
                return Schema__Link__Create__Response(success = False           ,
                                                      message = 'Link already exists')

        # Add links to nodes
        source_node.links.append(source_link)
        source_node.updated_at = now

        target_node.links.append(target_link)
        target_node.updated_at = now

        # Save both nodes
        if self.repository.node_save(source_node) is False:
            return Schema__Link__Create__Response(success = False                   ,
                                                  message = 'Failed to save source' )

        if self.repository.node_save(target_node) is False:
            # Rollback source (remove link we just added)
            source_node.links.remove(source_link)
            self.repository.node_save(source_node)
            return Schema__Link__Create__Response(success = False                   ,
                                                  message = 'Failed to save target' )

        return Schema__Link__Create__Response(success     = True        ,
                                              source_link = source_link ,
                                              target_link = target_link )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Link Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def delete_link(self                              ,                          # Delete bidirectional link
                    source_type  : Safe_Str__Node_Type   ,
                    source_label : Safe_Str__Node_Label  ,
                    target_label : Safe_Str__Node_Label
               ) -> Schema__Link__Delete__Response:
        # Load source node
        source_node = self.repository.node_load(node_type = source_type  ,
                                                label     = source_label )
        if source_node is None:
            return Schema__Link__Delete__Response(success = False                          ,
                                                  deleted = False                          ,
                                                  message = f'Source not found: {source_label}')

        # Find and remove the link from source
        link_to_remove = None
        for link in source_node.links:
            if str(link.target_label) == str(target_label):
                link_to_remove = link
                break

        if link_to_remove is None:
            return Schema__Link__Delete__Response(success = False          ,
                                                  deleted = False          ,
                                                  message = 'Link not found')

        # Parse target label
        target_type, parsed_target_label = self.parse_label(target_label)
        if target_type is None:
            return Schema__Link__Delete__Response(success = False                               ,
                                                  deleted = False                               ,
                                                  message = f'Invalid target label: {target_label}')

        # Load target node
        target_node = self.repository.node_load(node_type = target_type       ,
                                                label     = parsed_target_label)
        if target_node is None:
            return Schema__Link__Delete__Response(success = False                          ,
                                                  deleted = False                          ,
                                                  message = f'Target not found: {target_label}')

        # Remove link from source
        source_node.links.remove(link_to_remove)
        source_node.updated_at = Timestamp_Now()

        # Find and remove inverse link from target
        inverse_to_remove = None
        for link in target_node.links:
            if str(link.target_label) == str(source_label):
                inverse_to_remove = link
                break

        if inverse_to_remove:
            target_node.links.remove(inverse_to_remove)
            target_node.updated_at = Timestamp_Now()

        # Save both nodes
        self.repository.node_save(source_node)
        if inverse_to_remove:
            self.repository.node_save(target_node)

        return Schema__Link__Delete__Response(success      = True         ,
                                              deleted      = True         ,
                                              source_label = source_label ,
                                              target_label = target_label )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def find_link_type(self                        ,                             # Find link type by verb
                       verb : Safe_Str__Link_Verb
                  ) -> Optional[Schema__Link__Type]:
        link_types = self.repository.link_types_load()
        for lt in link_types:
            if str(lt.verb) == str(verb):
                return lt
        return None

    def parse_label(self                              ,                          # Parse label to (type, label)
                    label : Safe_Str__Node_Label
               ) -> tuple:
        # "Bug-27" → ("bug", "Bug-27")
        # "Task-15" → ("task", "Task-15")
        label_str = str(label)
        if '-' not in label_str:
            return (None, None)

        parts = label_str.split('-', 1)
        if len(parts) != 2:
            return (None, None)

        node_type = parts[0].lower()                                             # "Bug" → "bug"
        return (Safe_Str__Node_Type(node_type), label)
