# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Property__Definition - Definition of a type-specific property field
# Properties allow each node type to have its own custom fields
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import List
from enum                                                                        import Enum
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text     import Safe_Str__Text


class Enum__Property__Type(str, Enum):                                           # Property value types
    STRING   = "string"                                                          # Free text
    NUMBER   = "number"                                                          # Numeric value
    BOOLEAN  = "boolean"                                                         # True/false
    ENUM     = "enum"                                                            # Predefined options
    DATE     = "date"                                                            # ISO date string
    DATETIME = "datetime"                                                        # ISO datetime string


class Schema__Property__Definition(Type_Safe):                                   # Custom property definition
    name         : Safe_Str__Text                                                # Property name like "severity"
    prop_type    : Enum__Property__Type = Enum__Property__Type.STRING            # Value type
    description  : Safe_Str__Text                                                # What this property represents
    required     : bool                 = False                                  # Whether property is required
    options      : List[Safe_Str__Text]                                          # For ENUM type: valid options
    default      : Safe_Str__Text       = None                                   # Default value (optional)
