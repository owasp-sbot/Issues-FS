# ═══════════════════════════════════════════════════════════════════════════════
# Graph__Repository__Factory - Factory for creating graph repositories
# Provides easy setup for different storage backends (Memory, Local Disk, S3, etc.)
# ═══════════════════════════════════════════════════════════════════════════════

from memory_fs.Memory_FS                                                                         import Memory_FS
from memory_fs.helpers.Memory_FS__In_Memory                                                      import Memory_FS__In_Memory
from memory_fs.storage_fs.providers.Storage_FS__Local_Disk                                       import Storage_FS__Local_Disk
from memory_fs.storage_fs.providers.Storage_FS__Sqlite                                           import Storage_FS__Sqlite
from memory_fs.storage_fs.providers.Storage_FS__Zip                                              import Storage_FS__Zip
from osbot_utils.type_safe.Type_Safe                                                             import Type_Safe
from mgraph_ai_ui_html_transformation_workbench.schemas.enums.Enum__Graph__Storage__Backend      import Enum__Graph__Storage__Backend
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository  import Graph__Repository
from mgraph_ai_ui_html_transformation_workbench.service.issues.storage.Path__Handler__Graph_Node import Path__Handler__Graph_Node


class Graph__Repository__Factory(Type_Safe):                                     # Factory for graph repositories

    # ═══════════════════════════════════════════════════════════════════════════════
    # Memory Backend (for tests)
    # ═══════════════════════════════════════════════════════════════════════════════

    @classmethod
    def create_memory(cls) -> Graph__Repository:                                 # Create in-memory repository
        memory_fs    = Memory_FS__In_Memory()
        path_handler = Path__Handler__Graph_Node()
        return Graph__Repository(memory_fs    = memory_fs   ,
                                 path_handler = path_handler)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Local Disk Backend (for development / Git workflows)
    # ═══════════════════════════════════════════════════════════════════════════════

    @classmethod
    def create_local_disk(cls                              ,                     # Create local disk repository
                          root_path : str
                     ) -> Graph__Repository:
        memory_fs            = Memory_FS()
        storage              = Storage_FS__Local_Disk(root_path=str(root_path))
        memory_fs.storage_fs = storage
        path_handler         = Path__Handler__Graph_Node()
        return Graph__Repository(memory_fs    = memory_fs   ,
                                 path_handler = path_handler)

    # ═══════════════════════════════════════════════════════════════════════════════
    # SQLite Backend (for embedded use)
    # ═══════════════════════════════════════════════════════════════════════════════

    @classmethod
    def create_sqlite(cls                              ,                         # Create SQLite repository
                      db_path : str
                 ) -> Graph__Repository:
        memory_fs            = Memory_FS()
        storage              = Storage_FS__Sqlite(db_path=str(db_path))
        memory_fs.storage_fs = storage
        path_handler         = Path__Handler__Graph_Node()
        return Graph__Repository(memory_fs    = memory_fs   ,
                                 path_handler = path_handler)

    # ═══════════════════════════════════════════════════════════════════════════════
    # ZIP Backend (for archives/export)
    # ═══════════════════════════════════════════════════════════════════════════════

    @classmethod
    def create_zip(cls                              ,                            # Create ZIP repository
                   zip_path : str
              ) -> Graph__Repository:
        memory_fs            = Memory_FS()
        storage              = Storage_FS__Zip(zip_path=str(zip_path))
        memory_fs.storage_fs = storage
        path_handler         = Path__Handler__Graph_Node()
        return Graph__Repository(memory_fs    = memory_fs   ,
                                 path_handler = path_handler)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Generic Factory Method
    # ═══════════════════════════════════════════════════════════════════════════════

    @classmethod
    def create(cls                                                     ,         # Generic factory
               backend   : Enum__Graph__Storage__Backend               ,
               root_path : str                                  = None ,
               db_path   : str                                  = None ,
               zip_path  : str                                  = None
          ) -> Graph__Repository:

        if backend == Enum__Graph__Storage__Backend.MEMORY:
            return cls.create_memory()

        elif backend == Enum__Graph__Storage__Backend.LOCAL_DISK:
            if root_path is None:
                raise ValueError("root_path required for LOCAL_DISK backend")
            return cls.create_local_disk(root_path=root_path)

        elif backend == Enum__Graph__Storage__Backend.SQLITE:
            if db_path is None:
                raise ValueError("db_path required for SQLITE backend")
            return cls.create_sqlite(db_path=db_path)

        elif backend == Enum__Graph__Storage__Backend.ZIP:
            if zip_path is None:
                raise ValueError("zip_path required for ZIP backend")
            return cls.create_zip(zip_path=zip_path)

        else:
            raise ValueError(f"Unknown backend: {backend}")
