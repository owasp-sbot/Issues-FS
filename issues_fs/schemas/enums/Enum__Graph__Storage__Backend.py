from enum import Enum


class Enum__Graph__Storage__Backend(str, Enum):                                  # Available storage backends
    MEMORY     = "memory"                                                        # In-memory (tests)
    LOCAL_DISK = "local_disk"                                                    # Local file system
    SQLITE     = "sqlite"                                                        # SQLite database
    ZIP        = "zip"                                                           # ZIP archive
