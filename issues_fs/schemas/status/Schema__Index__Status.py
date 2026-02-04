# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Index__Status - Index and node statistics
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import List
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                             import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text     import Safe_Str__Text


class Schema__Type__Count(Type_Safe):                                            # Count for a single type
    node_type     : Safe_Str__Text      = ''                                     # Type name
    count         : Safe_UInt           = Safe_UInt(0)                           # Number of nodes
    next_index    : Safe_UInt           = Safe_UInt(1)                           # Next index to assign


class Schema__Index__Status(Type_Safe):                                          # Index statistics
    global_index_exists : bool                    = False                        # _index.json exists
    total_nodes         : Safe_UInt               = Safe_UInt(0)                 # Total across all types
    #total_links         : Safe_UInt               = Safe_UInt(0)                 # Total relationships
    type_counts         : List[Schema__Type__Count]                              # Per-type counts
    last_updated        : Safe_Str__Text          = ''                           # Last index update time
