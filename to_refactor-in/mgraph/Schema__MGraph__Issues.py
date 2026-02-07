# ═══════════════════════════════════════════════════════════════════════════════
# Schema__MGraph__Issues - Pure data schemas for MGraphDB issue storage
# Phase 2 (B18): Four-layer architecture - Schema Layer
#
# CRITICAL: Schema classes contain ONLY type annotations - NO methods
# Business logic belongs in MGraph__Issues__Domain
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import Dict, List
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                import Edge_Id
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text     import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status


class Schema__MGraph__Issue__Node(Type_Safe):                                    # Issue node data
    node_id   : Node_Id                                                          # Unique identifier
    label     : Safe_Str__Node_Label                                             # Display label (e.g., "Task-6")
    title     : Safe_Str__Text                                                   # Human-readable title
    node_type : Safe_Str__Node_Type                                              # Type (e.g., "task")
    status    : Safe_Str__Status                                                 # Current status
    file_path : Safe_Str__File__Path                                             # Filesystem path to issue.json folder


class Schema__MGraph__Issue__Edge(Type_Safe):                                    # Issue edge data
    edge_id   : Edge_Id                                                          # Unique identifier
    source_id : Node_Id                                                          # Source node ID
    target_id : Node_Id                                                          # Target node ID
    edge_type : Safe_Str__Text                                                   # 'contains', 'relates-to', etc.


class Schema__MGraph__Issues__Data(Type_Safe):                                   # Graph data container
    nodes : Dict[str, Schema__MGraph__Issue__Node] = None                        # node_id → node
    edges : Dict[str, Schema__MGraph__Issue__Edge] = None                        # edge_id → edge

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.nodes is None:
            self.nodes = {}
        if self.edges is None:
            self.edges = {}
