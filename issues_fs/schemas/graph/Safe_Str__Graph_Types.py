# ═══════════════════════════════════════════════════════════════════════════════
# Safe String Types for Graph-Based Issue Tracking
# Type-safe primitives for node types, labels, statuses, and verbs
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
from osbot_utils.type_safe.primitives.core.enums.Enum__Safe_Str__Regex_Mode     import Enum__Safe_Str__Regex_Mode


# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Node_Type - Node type identifier (bug, task, feature, person, etc.)
# ═══════════════════════════════════════════════════════════════════════════════

class Safe_Str__Node_Type(Safe_Str):                                             # Node type like "bug", "task"
    max_length        = 50
    regex             = re.compile(r'^[a-z][a-z0-9-]*$')                         # lowercase, hyphens allowed
    regex_mode        = Enum__Safe_Str__Regex_Mode.MATCH
    strict_validation = True


# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Node_Label - Human-readable node label (Bug-27, Task-15)
# ═══════════════════════════════════════════════════════════════════════════════

class Safe_Str__Node_Label(Safe_Str):                                            # Node label like "Bug-27"
    max_length        = 100
    regex             = re.compile(r'^[A-Z][a-zA-Z]*(-[A-Z][a-zA-Z]*)*-\d{1,5}$')  # Word(-Word)*-N (e.g., Git-Repo-1)
    regex_mode        = Enum__Safe_Str__Regex_Mode.MATCH
    strict_validation = True


# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Status - Status identifier (backlog, in-progress, done, etc.)
# ═══════════════════════════════════════════════════════════════════════════════

class Safe_Str__Status(Safe_Str):                                                # Status like "in-progress"
    max_length        = 50
    regex             = re.compile(r'^[a-z][a-z0-9-]*$')                         # lowercase, hyphens allowed
    regex_mode        = Enum__Safe_Str__Regex_Mode.MATCH
    strict_validation = True


# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Link_Verb - Relationship verb (blocks, has-task, assigned-to)
# ═══════════════════════════════════════════════════════════════════════════════

class Safe_Str__Link_Verb(Safe_Str):                                             # Link verb like "blocks"
    max_length        = 50
    regex             = re.compile(r'^[a-z][a-z0-9-]*$')                         # lowercase, hyphens allowed
    regex_mode        = Enum__Safe_Str__Regex_Mode.MATCH
    strict_validation = True


# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Node_Type_Display - Display name for node type (Bug, Task, Feature)
# ═══════════════════════════════════════════════════════════════════════════════

class Safe_Str__Node_Type_Display(Safe_Str):                                     # Display name like "Bug"
    max_length        = 100
    regex             = re.compile(r'^[A-Z][a-zA-Z0-9 ]*$')                      # Title case, spaces allowed
    regex_mode        = Enum__Safe_Str__Regex_Mode.MATCH
    strict_validation = True
