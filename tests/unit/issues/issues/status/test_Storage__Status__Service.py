# ═══════════════════════════════════════════════════════════════════════════════
# test_Storage__Status__Service - Unit tests for storage status introspection
# Tests storage backend detection, connectivity, and capability reporting
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                               import TestCase

from osbot_utils.testing.__ import __
from osbot_utils.utils.Files                                                                                import temp_folder, folder_delete_recursively
from memory_fs.storage_fs.providers.Storage_FS__Local_Disk                                                  import Storage_FS__Local_Disk
from memory_fs.storage_fs.providers.Storage_FS__Memory                                                      import Storage_FS__Memory
from issues_fs.schemas.status.Schema__Storage__Status                      import Schema__Storage__Status
from issues_fs.issues.status.Storage__Status__Service              import Storage__Status__Service



class test_Storage__Status__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup
        cls.root_path              = temp_folder()
        cls.storage_fs__memory     = Storage_FS__Memory()
        cls.storage_fs__disk       = Storage_FS__Local_Disk(root_path=cls.root_path)
        #cls.memory_fs             = Memory_FS             (storage_fs=cls.memory_storage)
        cls.storage_status__memory = Storage__Status__Service(storage_fs=cls.storage_fs__memory)
        cls.storage_status__disk   = Storage__Status__Service(storage_fs=cls.storage_fs__disk  )

    @classmethod
    def tearDownClass(cls):
        folder_delete_recursively(cls.root_path)

    def setUp(self):                                                             # Reset before each test
        self.storage_fs__memory.clear()                                         # todo: see if we need this
        self.storage_fs__disk.clear()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test service initialization
        service = Storage__Status__Service()
        assert type(service) is Storage__Status__Service

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_status Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_status__no_memory_fs(self):                                    # Test status when not configured
        service = Storage__Status__Service()

        status = service.get_status()

        assert type(status)         is Schema__Storage__Status
        assert str(status.backend_type) == 'not_configured'
        assert status.is_connected  is False

    def test__get_status__memory_backend(self):                                  # Test with memory backend
        with self.storage_status__memory as _:

            status = _.get_status()

            assert type(status)              is Schema__Storage__Status
            assert str(status.backend_type)  == 'Storage_FS__Memory'
            assert status.is_connected       is True

    def test__get_status__local_disk_backend(self):                              # Test with local disk backend
        with self.storage_status__disk as _:

            status = _.get_status()

            assert status.backend_type  == 'Storage_FS__Local_Disk'
            assert status.root_path     == self.root_path

    def test__get_status__is_writable(self):                                     # Test writable detection
        with self.storage_status__memory as _:
            status = _.get_status()

            assert status.is_writable is True

    def test__get_status__file_count(self):                                      # Test file counting
        with self.storage_status__memory as _:
            assert _.storage_fs.file__save('file1.json', b'{}') is True
            assert _.storage_fs.file__save('file2.json', b'{}') is True
            assert _.storage_fs.file__save('file3.json', b'{}') is True
            assert _.storage_fs.files__paths() == ['file1.json',
                                                   'file2.json',
                                                   'file3.json']


            status = _.get_status()
            assert status.obj() == __(backend_type='Storage_FS__Memory',
                                      root_path='',
                                      is_connected=True,
                                      is_writable=True,
                                      file_count=3)



    # ═══════════════════════════════════════════════════════════════════════════════
    # Root Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════


    def test___get_root_path__local_disk(self):                                  # Test root path for local disk
        with self.storage_status__disk as _:
            assert _._get_root_path()== self.root_path

    def test___get_root_path__memory(self):                                      # Test root path for memory
        with self.storage_status__memory as _:
            assert _._get_root_path() == ''


    # ═══════════════════════════════════════════════════════════════════════════════
    # Connectivity Tests
    # ═══════════════════════════════════════════════════════════════════════════════


    def test___check_connection__success(self):                                  # Test successful connection
        with self.storage_status__memory as _:
            assert _._check_connection() is True
            assert _._check_writable() is True                                   # Test writable success