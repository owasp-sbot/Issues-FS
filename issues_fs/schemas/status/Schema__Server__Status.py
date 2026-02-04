# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Server__Status - Comprehensive server status information
# Aggregates all status components into a single response
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now            import Timestamp_Now
from issues_fs.schemas.status.Schema__API__Info            import Schema__API__Info
from issues_fs.schemas.status.Schema__Git__Status          import Schema__Git__Status
from issues_fs.schemas.status.Schema__Index__Status        import Schema__Index__Status
from issues_fs.schemas.status.Schema__Storage__Status      import Schema__Storage__Status
from issues_fs.schemas.status.Schema__Types__Status        import Schema__Types__Status


class Schema__Server__Status(Type_Safe):                                         # Full server status
    timestamp         : Timestamp_Now                                            # Status check timestamp
    api               : Schema__API__Info       = None                           # API version info
    storage           : Schema__Storage__Status = None                           # Storage backend status
    types             : Schema__Types__Status   = None                           # Type configuration
    index             : Schema__Index__Status   = None                           # Index statistics
    git               : Schema__Git__Status     = None                           # Git integration status


class Schema__Server__Status__Response(Type_Safe):                               # API response wrapper
    success : bool                    = False                                    # Operation success
    status  : Schema__Server__Status  = None                                     # Full status data
    message : Safe_Str__Text          = ''                                       # Error message if failed
