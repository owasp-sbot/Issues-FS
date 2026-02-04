# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Git__Status - Git repository integration status
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import List
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                             import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text     import Safe_Str__Text


class Schema__Git__Status(Type_Safe):                                            # Git integration status
    is_git_repo       : bool                = False                              # Inside a git repository
    git_root          : Safe_Str__Text      = ''                                 # Git root directory
    current_branch    : Safe_Str__Text      = ''                                 # Current branch name
    current_commit    : Safe_Str__Text      = ''                                 # Current commit hash (short)
    is_dirty          : bool                = False                              # Has uncommitted changes
    issues_tracked    : bool                = False                              # .issues/ in git
    untracked_issues  : Safe_UInt           = Safe_UInt(0)                       # Untracked issue files
    modified_issues   : Safe_UInt           = Safe_UInt(0)                       # Modified issue files
    remote_name       : Safe_Str__Text      = ''                                 # Remote name (origin)
    remote_url        : Safe_Str__Text      = ''                                 # Remote URL # todo: this create an Type_Safe primitive that supports git urls  (which could have @)
