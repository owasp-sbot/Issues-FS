# ═══════════════════════════════════════════════════════════════════════════════
# Schema__API__Info - API version and build information
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text     import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version import Safe_Str__Version


class Schema__API__Info(Type_Safe):                                              # API version info
    version       : Safe_Str__Version   = ''                                     # Semantic version (e.g., "0.2.4")
    build_date    : Safe_Str__Text      = ''                                     # Build timestamp
    environment   : Safe_Str__Text      = ''                                     # dev, staging, production
    python_version: Safe_Str__Text      = ''                                     # Python runtime version
    api_name      : Safe_Str__Text      = ''                                     # API service name
