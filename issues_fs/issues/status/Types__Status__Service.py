# ═══════════════════════════════════════════════════════════════════════════════
# Types__Status__Service - Node and link type configuration status
# Reports on configured node types and link types
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                                 import List, Optional
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                        import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                                import Safe_Str__Text
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe

from mgraph_ai_ui_html_transformation_workbench.schemas.status.Schema__Types__Status                        import Schema__Types__Status, Schema__Node__Type__Summary, Schema__Link__Type__Summary
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Type__Service                 import Type__Service


class Types__Status__Service(Type_Safe):                                         # Types status service
    type_service : Type__Service = None                                          # Type__Service instance

    # ═══════════════════════════════════════════════════════════════════════════════
    # Main Status Method
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_status(self) -> Schema__Types__Status:                               # Get types status
        if self.type_service is None:
            return Schema__Types__Status(is_initialized = False                              )

        node_types   = self._get_node_type_summaries()
        link_types   = self._get_link_type_summaries()
        is_init      = len(node_types) > 0 or len(link_types) > 0

        return Schema__Types__Status(is_initialized   = is_init                              ,
                                     node_type_count  = Safe_UInt(len(node_types))           ,
                                     link_type_count  = Safe_UInt(len(link_types))           ,
                                     node_types       = node_types                           ,
                                     link_types       = link_types                           )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Types
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def _get_node_type_summaries(self) -> List[Schema__Node__Type__Summary]:     # Get node type summaries
        summaries = []

        node_types = self.type_service.list_node_types()
        if node_types:
            for note_type in node_types:
                status_count = len(note_type.statuses)
                summary = Schema__Node__Type__Summary(name         = note_type.name        ,
                                                      display_name = note_type.display_name,
                                                      color        = note_type.color       ,
                                                      status_count = status_count   )
                summaries.append(summary)


        return summaries

    # ═══════════════════════════════════════════════════════════════════════════════
    # Link Types
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def _get_link_type_summaries(self) -> List[Schema__Link__Type__Summary]:     # Get link type summaries
        summaries = []


        link_types = self.type_service.list_link_types()
        if link_types:
            for link_type in link_types:

                summary = Schema__Link__Type__Summary(verb         = link_type.verb                           ,
                                                      inverse_verb = link_type.inverse_verb                   ,
                                                      is_symmetric = link_type.verb == link_type.inverse_verb ) # todo: review the use of this, and if we need this, why we are mapping is_symmetric in Schema__Link__Type__Summary and not in Schema__Link__Type
                summaries.append(summary)
        return summaries
