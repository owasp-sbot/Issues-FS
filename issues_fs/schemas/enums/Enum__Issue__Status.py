# ═══════════════════════════════════════════════════════════════════════════════
# Enum__Issue__Status - Issue status enumeration
# ═══════════════════════════════════════════════════════════════════════════════

from enum                                                                       import Enum


class Enum__Issue__Status(str, Enum):                                            # Issue status values
    BACKLOG     = "backlog"
    TODO        = "todo"
    IN_PROGRESS = "in-progress"
    REVIEW      = "review"
    DONE        = "done"
