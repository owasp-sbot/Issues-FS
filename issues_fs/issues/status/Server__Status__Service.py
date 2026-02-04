# ═══════════════════════════════════════════════════════════════════════════════
# Server__Status__Service - Main server status orchestrator
# Aggregates all status components into a comprehensive response
# ═══════════════════════════════════════════════════════════════════════════════

import sys
from datetime                                                                                               import datetime
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                                import Safe_Str__Text
from issues_fs.schemas.status.Schema__API__Info                            import Schema__API__Info
from issues_fs.schemas.status.Schema__Server__Status                       import Schema__Server__Status
from issues_fs.schemas.status.Schema__Server__Status                       import Schema__Server__Status__Response
from issues_fs.issues.status.Git__Status__Service                  import Git__Status__Service
from issues_fs.issues.status.Index__Status__Service                import Index__Status__Service
from issues_fs.issues.status.Storage__Status__Service              import Storage__Status__Service
from issues_fs.issues.status.Types__Status__Service                import Types__Status__Service
from issues_fs.utils.Version                                               import version__issues_fs

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration Constants
# ═══════════════════════════════════════════════════════════════════════════════

API_VERSION     = '0.2.4'
API_NAME        = 'Graph Issue Tracking API'
BUILD_DATE      = 'NA'                              # see if we can get this from the .git folder
ENVIRONMENT     = 'development'


class Server__Status__Service(Type_Safe):                                        # Main status service
    storage_service : Storage__Status__Service  = None                           # Storage status
    git_service     : Git__Status__Service      = None                           # Git status
    types_service   : Types__Status__Service    = None                           # Types status
    index_service   : Index__Status__Service    = None                           # Index status

    # ═══════════════════════════════════════════════════════════════════════════════
    # Main Status Method
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_full_status(self) -> Schema__Server__Status__Response:               # Get comprehensive status

        timestamp      = self._get_timestamp()
        api_info       = self._get_api_info()
        storage_status = self._get_storage_status()
        git_status     = self._get_git_status()
        types_status   = self._get_types_status()
        index_status   = self._get_index_status()

        status = Schema__Server__Status(timestamp      = Safe_Str__Text(timestamp)       ,
                                        api            = api_info                        ,
                                        storage        = storage_status                  ,
                                        types          = types_status                    ,
                                        index          = index_status                    ,
                                        git            = git_status                      )

        return Schema__Server__Status__Response(success = True                           ,
                                                status  = status                         )

        # except Exception as e:
        #     return Schema__Server__Status__Response(success = False                          ,
        #                                             message = Safe_Str__Text(f'Error: {str(e)}'))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Individual Status Getters
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_api_info(self) -> Schema__API__Info:                                 # Public API info getter
        return self._get_api_info()

    def get_storage_status(self):                                                # Public storage status
        return self._get_storage_status()

    def get_git_status(self):                                                    # Public git status
        return self._get_git_status()

    def get_types_status(self):                                                  # Public types status
        return self._get_types_status()

    def get_index_status(self):                                                  # Public index status
        return self._get_index_status()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Private Status Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _get_timestamp(self) -> str:                                             # Get current timestamp
        return datetime.utcnow().isoformat() + 'Z'

    def _get_api_info(self) -> Schema__API__Info:                                # Build API info
        return Schema__API__Info(version        = version__issues_fs                ,
                                 build_date     = Safe_Str__Text(BUILD_DATE)                 ,
                                 environment    = Safe_Str__Text(ENVIRONMENT)                ,
                                 python_version = Safe_Str__Text(sys.version.split()[0])     ,
                                 api_name       = Safe_Str__Text(API_NAME)                   )

    def _get_storage_status(self):                                               # Get storage status
        if self.storage_service:
            return self.storage_service.get_status()
        return None

    def _get_git_status(self):                                                   # Get git status
        if self.git_service:
            return self.git_service.get_status()
        return None

    def _get_types_status(self):                                                 # Get types status
        if self.types_service:
            return self.types_service.get_status()
        return None

    def _get_index_status(self):                                                 # Get index status
        if self.index_service:
            return self.index_service.get_status()
        return None
