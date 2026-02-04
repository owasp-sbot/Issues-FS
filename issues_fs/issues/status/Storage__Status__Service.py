# ═══════════════════════════════════════════════════════════════════════════════
# Storage__Status__Service - Storage backend introspection
# Inspects Memory-FS configuration and provides detailed status
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                                import Safe_Str__Text
from memory_fs.storage_fs.Storage_FS                                                                        import Storage_FS
from mgraph_ai_ui_html_transformation_workbench.schemas.status.Schema__Storage__Status                      import Schema__Storage__Status


class Storage__Status__Service(Type_Safe):                                       # Storage status service
    storage_fs : Storage_FS = None                                                 # Storage_FS instance

    # ═══════════════════════════════════════════════════════════════════════════════
    # Main Status Method
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_status(self) -> Schema__Storage__Status:                             # Get storage status
        if self.storage_fs is None:
            return Schema__Storage__Status(backend_type  = Safe_Str__Text('not_configured'),
                                           is_connected  = False                            )

        backend_type  = type(self.storage_fs).__name__

        return Schema__Storage__Status(backend_type   = backend_type            ,
                                       root_path      = self._get_root_path   (),
                                       is_connected   = self._check_connection(),
                                       is_writable    = self._check_writable  (),
                                       file_count     = self._count_files     ())

    def _get_root_path(self) -> str:                                 # Get configured root path

        path_attrs = ['root_path', 'db_path', 'zip_path', 'bucket', 'base_path']
        for attr in path_attrs:
            if hasattr(self.storage_fs, attr):
                value = getattr(self.storage_fs, attr, None)
                if value:
                    return str(value)
        return ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # Connectivity Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _check_connection(self) -> bool:                             # Test read connectivity
        self.storage_fs.file__exists('__connectivity_test__')
        return True

    def _check_writable(self) -> bool:                               # Test write connectivity
        with self.storage_fs as _:
            test_path = '__write_test_temp__'
            test_data = b'test'

            if _.file__save(test_path, test_data):
                if _.file__delete(test_path):
                    return True
            return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Statistics Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _count_files(self) -> int:                                   # Count stored files
        return len(self.storage_fs.files__paths())

    def _count_folders(self) -> int:                                        # Count folders
        for method_name in ['folders__all', 'folders', 'list_folders']:     # todo: find a better way to do this
            if hasattr(self.storage_fs, method_name):
                method = getattr(self.storage_fs, method_name)
                if callable(method):
                    result = method()
                    if result:
                        return len(result)
        return 0
