# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Issue_Id - Type-safe issue identifier in Issue-NNN format
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
from osbot_utils.type_safe.primitives.core.enums.Enum__Safe_Str__Regex_Mode     import Enum__Safe_Str__Regex_Mode


class Safe_Str__Issue_Id(Safe_Str):                                                 # Issue ID in Issue-NNN format
    max_length        = 20
    regex             = re.compile(r'^[Ii]ssue-\d{1,5}$')
    regex_mode        = Enum__Safe_Str__Regex_Mode.MATCH                            # Pattern defines VALID format
    strict_validation = True                                                        # Required with MATCH mode
