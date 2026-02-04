# ═══════════════════════════════════════════════════════════════════════════════
# Enum__Comment__Author - Comment author enumeration
# ═══════════════════════════════════════════════════════════════════════════════

from enum                                                                       import Enum


class Enum__Comment__Author(str, Enum):                                          # Comment author values
    HUMAN       = "human"
    CLAUDE_CODE = "claude-code"
