# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Multiline - Safe string type that preserves newlines
# For description fields, comments, and other multiline text content
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                         import Safe_Str
from osbot_utils.type_safe.primitives.core.enums.Enum__Safe_Str__Regex_Mode import Enum__Safe_Str__Regex_Mode


class Safe_Str__Issue__Node__Description(Safe_Str):                                # Multiline text (preserves newlines)
    max_length        = 50000                                                # Allow long descriptions
    regex             = re.compile(r'[^\x20-\x7E\n\r\t]')                    # Allow printable ASCII + newlines + tabs
    regex_mode        = Enum__Safe_Str__Regex_Mode.REPLACE                   # Replace invalid chars
    allow_empty       = True                                                 # Empty is valid