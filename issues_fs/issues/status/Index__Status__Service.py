# ═══════════════════════════════════════════════════════════════════════════════
# Index__Status__Service - Index and node count statistics
# Reports on global index and per-type node counts
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                                 import List
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                        import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                                import Safe_Str__Text
from issues_fs.schemas.status.Schema__Index__Status                        import Schema__Index__Status
from issues_fs.schemas.status.Schema__Index__Status                        import Schema__Type__Count
from issues_fs.issues.graph_services.Graph__Repository             import Graph__Repository
from issues_fs.issues.graph_services.Type__Service                 import Type__Service

# todo: see why we are using type_service below and not index_service

class Index__Status__Service(Type_Safe):                                         # Index status service
    repository   : Graph__Repository = None                                      # Graph__Repository instance
    type_service : Type__Service = None                                          # Type__Service instance

    # ═══════════════════════════════════════════════════════════════════════════════
    # Main Status Method
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_status(self) -> Schema__Index__Status:                               # Get index status
        if self.repository is None:
            return Schema__Index__Status(global_index_exists = False             ,
                                         type_counts         = []                )

        global_exists = self._check_global_index_exists()
        type_counts   = self._get_type_counts()
        total_nodes   = self._calculate_total_nodes(type_counts)
        #total_links   = self._count_total_links()
        last_updated  = self._get_last_updated()

        return Schema__Index__Status(global_index_exists = global_exists                     ,
                                     total_nodes         = Safe_UInt(total_nodes)            ,
                                     #total_links         = Safe_UInt(total_links)            ,
                                     type_counts         = type_counts                       ,
                                     last_updated        = Safe_Str__Text(last_updated)      )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Index Checks
    # ═══════════════════════════════════════════════════════════════════════════════

    def _check_global_index_exists(self) -> bool:                                # Check global index exists
        index = self.repository.global_index_load()
        return index is not None

    def _get_last_updated(self) -> str:                                          # Get last update timestamp
        try:
            if hasattr(self.repository, 'global_index_load'):
                index = self.repository.global_index_load()
                if index and hasattr(index, 'last_updated'):
                    return str(index.last_updated or '')
        except Exception:
            pass
        return ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # Type Counts
    # ═══════════════════════════════════════════════════════════════════════════════


    def _get_type_counts(self) -> List[Schema__Type__Count]:                     # Get per-type counts
        counts = []


        # Get list of node types
        node_type_names = self._get_node_type_names()

        for type_name in node_type_names:
            type_count  = self._get_count_for_type(type_name)
            next_index  = self._get_next_index_for_type(type_name)

            counts.append(Schema__Type__Count(node_type  = type_name     ,
                                              count      = type_count    ,
                                              next_index = next_index    ))

        return counts

    def _get_node_type_names(self) -> List[str]:                                 # Get all node type names
        names = []

        node_types = self.type_service.list_node_types()
        if node_types:
            for node_type in node_types:
                name = node_type.name
                if name:
                    names.append(name)
        return names

    def _get_count_for_type(self, type_name: str) -> int:                        # Get node count for type
        try:
            if hasattr(self.repository, 'type_index_load'):
                type_index = self.repository.type_index_load(type_name)
                if type_index and hasattr(type_index, 'count'):
                    return int(type_index.count)
        except Exception:
            pass
        return 0

    def _get_next_index_for_type(self, type_name: str) -> int:                   # Get next index for type
        try:
            if hasattr(self.repository, 'type_index_load'):
                type_index = self.repository.type_index_load(type_name)
                if type_index and hasattr(type_index, 'next_index'):
                    return int(type_index.next_index)
        except Exception:
            pass
        return 1

    def _calculate_total_nodes(self, type_counts: List[Schema__Type__Count]) -> int:  # Sum all counts
        total = 0
        for tc in type_counts:
            total += int(tc.count)
        return total

    # # ═══════════════════════════════════════════════════════════════════════════════
    # # Link Counts
    # # ═══════════════════════════════════════════════════════════════════════════════
    #
    # def _count_total_links(self) -> int:                                         # Count total links
    #     total = 0
    #     try:
    #         # This would require loading all nodes and counting links
    #         # For now, return 0 - can be enhanced to iterate nodes
    #         pass
    #     except Exception:
    #         pass
    #     return total
