# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Node - Base node structure for graph-based issue tracking
# All entities (bugs, tasks, features, people) are nodes with typed relationships
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                         import List, Dict, Any
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                        import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                   import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                    import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                    import Timestamp_Now
from issues_fs.schemas.graph.Safe_Str__Graph_Types                 import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status
from issues_fs.schemas.graph.Schema__Node__Link                    import Schema__Node__Link
from issues_fs.schemas.safe_str.Safe_Str__Issue__Node__Description import Safe_Str__Issue__Node__Description


# todo: refactor all these classes to use 'Issue' since that is the generic name for this
#       for example this class should be called 'Schema__Issue__Node'
class Schema__Node(Type_Safe):                                                   # Base node structure for all entities
    node_id       : Node_Id                                                       # Random 10-char GUID for machine use
    node_type     : Safe_Str__Node_Type                                          # Classification: bug, task, feature, person
    node_index    : Safe_UInt                                                    # Per-type sequential number
    label         : Safe_Str__Node_Label                                         # Human-readable: "Bug-27", "Task-15"

    # todo: create Safe_Str__Issue__Node__Title  to use here
    title         : Safe_Str__Text                                               # Display title
    description   : Safe_Str__Issue__Node__Description                                 # Detailed description
    status        : Safe_Str__Status                                             # Current status (type-specific)

    created_at    : Timestamp_Now                                                # ISO timestamp created
    updated_at    : Timestamp_Now                                                # ISO timestamp updated
    # todo: see what is the best class to use here (Persona_Id , Creator_Id)
    #             : this should be an id created_by__id and the created_by should be name
    created_by    : Obj_Id                                                       # Person/agent node_id who created

    # todo: refactor these to use Type_Safe collections, and this should be Safe_Str__Issue__Tag
    tags          : List[Safe_Str__Text]                                         # Tags/categories (renamed from labels to avoid confusion)
    # todo: rename to Schema__Issue__Node__Link
    links         : List[Schema__Node__Link]                                     # Relationships to other nodes

    # todo: this should be an Type_Safe collection and we shouldn't be using raw primitives like str, Any
    properties    : Dict[str, Any]                                               # Type-specific properties (severity, browser, etc.)
