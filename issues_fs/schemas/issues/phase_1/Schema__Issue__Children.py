# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Issue__Children - Request/response schemas for child issue operations
# Phase 1: Supports adding children and converting to hierarchical structure
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                  import List
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                         import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                 import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path            import Safe_Str__File__Path

# todo: refactor all/most of the the Safe_Str__Text into domain specific type safe primitives

# ═══════════════════════════════════════════════════════════════════════════════
# Create Child Request
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Issue__Child__Create(Type_Safe):                                   # Request to create child issue
    issue_type  : Safe_Str__Text                                                 # Type: task, bug, feature, etc.
    title       : Safe_Str__Text                                                 # Issue title
    description : Safe_Str__Text                                                 # Optional description
    status      : Safe_Str__Text                                                 # Optional status (defaults to type's default)


# ═══════════════════════════════════════════════════════════════════════════════
# Child Issue Response
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Issue__Child__Response(Type_Safe):                                 # Response after creating child
    success    : bool
    path       : Safe_Str__File__Path                                            # Relative path to child
    label      : Safe_Str__Text                                                  # Generated label (e.g., "Task-1")
    issue_type : Safe_Str__Text                                                  # Issue type
    title      : Safe_Str__Text                                                  # Issue title
    message    : Safe_Str__Text                                                  # Error message if failed


# ═══════════════════════════════════════════════════════════════════════════════
# Child Summary (for list response)
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Issue__Child__Summary(Type_Safe):                                  # Summary of a child issue
    path       : Safe_Str__File__Path                                            # Relative path
    label      : Safe_Str__Text                                                  # Issue label
    title      : Safe_Str__Text                                                  # Issue title
    issue_type : Safe_Str__Text                                                  # Issue type
    status     : Safe_Str__Text = ''                                             # Current status


# ═══════════════════════════════════════════════════════════════════════════════
# List Children Response
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Issue__Children__List__Response(Type_Safe):                        # Response listing children
    success  : bool                  = False
    children : List[dict]            = None                                      # List of child summaries
    total    : Safe_UInt             = Safe_UInt(0)                              # Total count
    message  : Safe_Str__Text        = ''                                        # Error message if failed


# ═══════════════════════════════════════════════════════════════════════════════
# Convert to New Structure Response
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Issue__Convert__Response(Type_Safe):                                  # Response after converting issue
    success     : bool
    converted   : bool                                                              # True if actually converted (vs already had issues/)
    issues_path : Safe_Str__File__Path                                              # Path to issues/ folder
    message     : Safe_Str__Text                                                    # Status message


class Schema__Add_Child__Request(Type_Safe):                                     # Request body for adding child
    parent_path : Safe_Str__File__Path                                           # Path to parent issue
    issue_type  : Safe_Str__Text                                                 # Child issue type
    title       : Safe_Str__Text                                                 # Child title
    description : Safe_Str__Text = ''                                            # Optional description
    status      : Safe_Str__Text = ''                                            # Optional status


class Schema__List_Children__Request(Type_Safe):                                 # Request for listing children
    parent_path : Safe_Str__File__Path                                           # Path to parent issue


class Schema__Convert__Request(Type_Safe):                                       # Request for converting issue
    issue_path : Safe_Str__File__Path                                            # Path to issue to convert
