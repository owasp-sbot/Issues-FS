# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Graph__Response - Response types for graph traversal API
# Used by GET /nodes/api/nodes/{type}/{label}/graph endpoint
# ═══════════════════════════════════════════════════════════════════════════════
from typing                                                                         import List
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text        import Safe_Str__Text
from issues_fs.schemas.graph.Safe_Str__Graph_Types import Safe_Str__Node_Label
from issues_fs.schemas.graph.Schema__Graph__Link   import Schema__Graph__Link
from issues_fs.schemas.graph.Schema__Graph__Node   import Schema__Graph__Node



class Schema__Graph__Response(Type_Safe):                                        # Full graph traversal response
    success   : bool                      = False
    root      : Safe_Str__Node_Label      = None
    nodes     : List[Schema__Graph__Node] = None
    links     : List[Schema__Graph__Link] = None
    depth     : Safe_UInt                 = 0
    message   : Safe_Str__Text            = ''