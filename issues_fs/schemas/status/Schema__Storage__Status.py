# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Storage__Status - Memory-FS storage backend information
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import List
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                             import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text     import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path


class Schema__Storage__Capability(Type_Safe):                                    # Single capability info
    name          : Safe_Str__Text      = ''                                     # Capability name
    supported     : bool                = False                                  # Whether supported
    description   : Safe_Str__Text      = ''                                     # What it does


class Schema__Storage__Status(Type_Safe):                        # Memory-FS status info
    backend_type  : Safe_Str__Text                               # memory, local_disk, sqlite, zip
    root_path     : Safe_Str__File__Path = None                  # Root path (if applicable)
    is_connected  : bool                                         # Storage accessible
    is_writable   : bool                                         # Can write to storage
    file_count    : Safe_UInt                                    # Number of files
