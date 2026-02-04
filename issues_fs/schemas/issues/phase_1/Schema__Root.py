# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Root - Data types for root selection feature
# Phase 1: Allows any folder with issue.json/node.json to be selected as root
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                  import List
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                         import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                 import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path

from issues_fs.schemas.graph.Safe_Str__Graph_Types          import Safe_Str__Node_Type, Safe_Str__Node_Label


# ═══════════════════════════════════════════════════════════════════════════════
# Root Candidate Schema
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Root__Candidate(Type_Safe):                                        # A folder that can serve as root
    path        : Safe_Str__File__Path                                           # Relative path from .issues/
    label       : Safe_Str__Text                                                 # Issue label or "Root"
    title       : Safe_Str__Text                                                 # Issue title for display
    issue_type  : Safe_Str__Text                                                 # bug, task, feature, git-repo, etc.
    depth       : Safe_UInt          = Safe_UInt(0)                              # Nesting depth from .issues/
    has_issues  : bool               = False                                     # Has issues/ subfolder (new arch)
    has_children: Safe_UInt          = Safe_UInt(0)                              # Count of child issues


# ═══════════════════════════════════════════════════════════════════════════════
# Request Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Root__Select__Request(Type_Safe):                                  # Request to select a root
    path : Safe_Str__File__Path                                                  # Path to select as root


# ═══════════════════════════════════════════════════════════════════════════════
# Response Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Root__Current__Response(Type_Safe):                                # Current root response
    success      : bool
    path         : Safe_Str__File__Path                                          # Current root path
    label        : Safe_Str__Text                                                # Current root label
    issue_type   : Safe_Str__Text                                                # Current root type
    message      : Safe_Str__Text


class Schema__Root__List__Response(Type_Safe):                                   # List of root candidates
    success      : bool
    roots        : List[Schema__Root__Candidate]     = None
    total        : Safe_UInt
    message      : Safe_Str__Text


class Schema__Root__Select__Response(Type_Safe):                                 # Response after selecting root
    success      : bool
    path         : Safe_Str__File__Path                                          # Selected path
    previous     : Safe_Str__File__Path                                          # Previous root path
    message      : Safe_Str__Text