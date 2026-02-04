import memory_fs
from unittest                      import TestCase
from osbot_utils.utils.Files       import parent_folder, file_name
from memory_fs.utils.Version       import Version, version__memory_fs


class test_Version(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.version = Version()

    def test_path_code_root(self):
        assert self.version.path_code_root() == memory_fs.path

    def test_path_version_file(self):
        with self.version as _:
            assert parent_folder(_.path_version_file()) == memory_fs.path
            assert file_name    (_.path_version_file()) == 'version'

    def test_value(self):
        assert self.version.value() == version__memory_fs