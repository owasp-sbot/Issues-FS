# ═══════════════════════════════════════════════════════════════════════════════
# Schema__MGraph__Issues__Data - Graph data container schema
# Phase 2 (B18): Four-layer architecture - Schema Layer
#
# CRITICAL: Schema classes contain ONLY type annotations - NO methods
# Business logic belongs in MGraph__Issues__Domain
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                         import Dict
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from issues_fs.mgraph.Schema__MGraph__Issue__Node                                                   import Schema__MGraph__Issue__Node
from issues_fs.mgraph.Schema__MGraph__Issue__Edge                                                   import Schema__MGraph__Issue__Edge

class Schema__MGraph__Issues__Data(Type_Safe):                                   # Graph data container  # Bug-8: use Node_Id/Edge_Id keys, remove __init__
    nodes : Dict[str, Schema__MGraph__Issue__Node]                               # node_id -> node  # Bug-8: key should be Node_Id
    edges : Dict[str, Schema__MGraph__Issue__Edge]                               # edge_id -> edge  # Bug-8: key should be Edge_Id
