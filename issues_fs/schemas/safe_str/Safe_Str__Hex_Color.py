import re
from osbot_utils.type_safe.primitives.core.Safe_Str                                import Safe_Str
from osbot_utils.type_safe.primitives.core.enums.Enum__Safe_Str__Regex_Mode        import Enum__Safe_Str__Regex_Mode


class Safe_Str__Hex_Color(Safe_Str):                                               # Hex color like #22c55e
    max_length        = 7
    regex             = re.compile(r'^#[0-9A-Fa-f]{6}$')
    regex_mode        = Enum__Safe_Str__Regex_Mode.MATCH                           # Pattern defines VALID format
    strict_validation = True                                                       # Required with MATCH mode