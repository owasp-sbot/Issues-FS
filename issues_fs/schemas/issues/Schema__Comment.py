# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Comment - Data types for comments on nodes
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import List, Optional
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                 import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text     import Safe_Str__Text


# ═══════════════════════════════════════════════════════════════════════════════
# Comment Schema
# ═══════════════════════════════════════════════════════════════════════════════

# todo: this should be Schema__Issue__Comment
#       refactor each of these files into a separate schema file
#       change id to comment_id
class Schema__Comment(Type_Safe):                                                # Single comment on a node
    id         : Obj_Id                                                          # Unique comment ID
    author     : Safe_Str__Text                                                  # Who wrote it: 'human', 'claude-code', etc.
    text       : Safe_Str__Text                                                  # Comment content (supports markdown)
    created_at : Timestamp_Now                                                   # When created
    updated_at : Timestamp_Now                                                   # When last edited


# ═══════════════════════════════════════════════════════════════════════════════
# Request Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Comment__Create__Request(Type_Safe):                               # Create comment request
    author     : Safe_Str__Text                                                  # Who is writing
    text       : Safe_Str__Text                                                  # Comment content


class Schema__Comment__Update__Request(Type_Safe):                               # Update comment request
    text       : Safe_Str__Text                                                  # New comment content


# ═══════════════════════════════════════════════════════════════════════════════
# Response Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Comment__Response(Type_Safe):                                      # Single comment response
    success    : bool              = False
    comment    : Schema__Comment   = None
    message    : str               = ''


class Schema__Comment__List__Response(Type_Safe):                                # List comments response
    success    : bool                   = False
    comments   : List[Schema__Comment]  = None
    total      : int                    = 0
    message    : str                    = ''


class Schema__Comment__Delete__Response(Type_Safe):                              # Delete comment response
    success    : bool   = False
    deleted    : bool   = False
    comment_id : str    = ''
    message    : str    = ''